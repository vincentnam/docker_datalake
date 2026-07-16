"""Connecteur d'authentification entre Flask et JupyterHub."""

import hashlib
import os
import secrets
import sqlite3
import time

from flask import Blueprint, current_app, jsonify, request

from . import AuthenticationBackendError, AuthenticationRejected, get_auth


jupyter_auth_blueprint = Blueprint("jupyter_auth", __name__)


class JupyterTicketStore:
    """Stockage local des tickets SSO à usage unique."""

    # Un ticket est une preuve temporaire que Flask a déjà authentifié le user.
    # Flask le donne au navigateur qui le transmet à JupyterHub. JupyterHub le
    # renvoie ensuite à Flask pour récupérer uniquement l'identité du user.
    # Il ne contient pas le token Keystone, expire rapidement et ne fonctionne
    # qu'une seule fois. Cela évite d'exposer le token Keystone à JupyterHub ou
    # dans l'URL de redirection.
    # Ce ticket n'est pas fourni nativement par JupyterHub : c'est notre pont
    # entre Flask et l'Authenticator personnalisé de JupyterHub. Le mécanisme
    # reprend le principe d'un service ticket CAS : valeur opaque, durée courte
    # et une seule validation possible.
    # Service ticket CAS :
    # https://apereo.github.io/cas/development/protocol/CAS-Protocol-Specification.html#31-service-ticket
    # Authenticator JupyterHub :
    # https://jupyterhub.readthedocs.io/en/stable/reference/authenticators.html

    DEFAULT_DATABASE = "/tmp/datalake-jupyter-sso.sqlite3"
    DEFAULT_VALIDITY_SECONDS = 60
    MINIMUM_VALIDITY_SECONDS = 10
    MAXIMUM_VALIDITY_SECONDS = 300

    def __init__(self, database_path=None, validity_seconds=None):
        self.database_path = database_path or os.getenv(
            "JUPYTER_SSO_TICKET_DB",
            self.DEFAULT_DATABASE,
        )
        self.validity_seconds = (
            self._get_configured_validity_seconds()
            if validity_seconds is None
            else validity_seconds
        )

    def _get_configured_validity_seconds(self):
        try:
            validity_seconds = int(os.getenv(
                "JUPYTER_SSO_TICKET_TTL",
                self.DEFAULT_VALIDITY_SECONDS,
            ))
        except ValueError:
            validity_seconds = self.DEFAULT_VALIDITY_SECONDS
        return max(
            self.MINIMUM_VALIDITY_SECONDS,
            min(validity_seconds, self.MAXIMUM_VALIDITY_SECONDS),
        )

    def _connect(self):
        connection = sqlite3.connect(self.database_path, timeout=5)
        # La table est créée ici pour garder le connecteur autonome au démarrage.
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS jupyter_sso_tickets (
                digest TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                username TEXT NOT NULL,
                expires_at INTEGER NOT NULL
            )
            """
        )
        return connection

    @staticmethod
    def _hash_ticket(ticket):
        return hashlib.sha256(ticket.encode("utf-8")).hexdigest()

    def issue(self, user_id, username):
        ticket = secrets.token_urlsafe(32)
        current_timestamp = int(time.time())

        with self._connect() as connection:
            # On nettoie les anciens tickets avant d'en ajouter un nouveau.
            connection.execute(
                "DELETE FROM jupyter_sso_tickets WHERE expires_at < ?",
                (current_timestamp,),
            )
            connection.execute(
                """
                INSERT INTO jupyter_sso_tickets
                    (digest, user_id, username, expires_at)
                VALUES (?, ?, ?, ?)
                """,
                (
                    # Seul le hash est stocké : la valeur envoyée au navigateur
                    # ne peut pas être reconstruite depuis la base.
                    self._hash_ticket(ticket),
                    user_id,
                    username,
                    current_timestamp + self.validity_seconds,
                ),
            )

        return ticket

    def redeem(self, ticket):
        """Consomme le ticket dans une transaction pour empêcher le rejeu."""
        current_timestamp = int(time.time())
        ticket_hash = self._hash_ticket(ticket)
        connection = self._connect()

        try:
            # Le SELECT et le DELETE sont dans la même transaction. Deux appels
            # simultanés ne peuvent donc pas utiliser le même ticket.
            connection.execute("BEGIN IMMEDIATE")
            ticket_record = connection.execute(
                """
                SELECT user_id, username, expires_at
                FROM jupyter_sso_tickets
                WHERE digest = ?
                """,
                (ticket_hash,),
            ).fetchone()
            connection.execute(
                """
                DELETE FROM jupyter_sso_tickets
                WHERE digest = ? OR expires_at < ?
                """,
                (ticket_hash, current_timestamp),
            )
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

        if ticket_record is None or ticket_record[2] < current_timestamp:
            return None

        return {
            "id": ticket_record[0],
            "username": ticket_record[1],
            "source": "keystone_sso",
        }


@jupyter_auth_blueprint.route("/auth/jupyter/local", methods=["POST"])
def jupyter_local_login():
    """Authentifie un compte Keystone local via le backend Flask configuré."""
    request_payload = request.get_json(silent=True) or {}
    username = request_payload.get("username")
    password = request_payload.get("password")

    if not isinstance(username, str) or not username.strip():
        return jsonify({"error": "Invalid credentials"}), 401
    if not isinstance(password, str) or not password:
        return jsonify({"error": "Invalid credentials"}), 401
    if len(username) > 255 or len(password) > 4096:
        return jsonify({"error": "Invalid credentials"}), 401

    username = username.strip()

    # JupyterHub ne connaît pas Keystone : il délègue la vérification au backend
    # d'authentification déjà utilisé par Flask.
    try:
        authentication_backend = os.getenv(
            "AUTHENTICATION_BACKEND",
            "openstack",
        )
        authenticated_user = get_auth(
            authentication_backend
        ).authenticate_credentials(username, password)
    except AuthenticationRejected:
        return jsonify({"error": "Invalid credentials"}), 401
    except AuthenticationBackendError as exception:
        current_app.logger.warning(
            "JupyterHub local authentication failed for user %s: %s",
            username,
            type(exception).__name__,
        )
        return jsonify({"error": "Authentication service unavailable"}), 503
    except Exception as exception:
        current_app.logger.exception(
            "Unexpected JupyterHub authentication error for user %s: %s",
            username,
            type(exception).__name__,
        )
        return jsonify({"error": "Authentication service unavailable"}), 503

    # On retourne uniquement l'identité utile à JupyterHub, jamais le token
    # Keystone ni le mot de passe.
    return jsonify({
        "authenticated": True,
        "user": {
            "id": authenticated_user["id"],
            "username": authenticated_user["username"],
            "source": "keystone_local",
        },
    }), 200


@jupyter_auth_blueprint.route("/auth/jupyter/ticket", methods=["POST"])
def jupyter_ticket_login():
    """Échange un ticket SSO contre l'identité attendue par JupyterHub."""
    request_payload = request.get_json(silent=True) or {}
    ticket = request_payload.get("ticket")

    if not isinstance(ticket, str) or not ticket or len(ticket) > 512:
        return jsonify({"error": "Invalid or expired ticket"}), 401

    # Le ticket est consommé ici, il ne peut pas être rejoué ensuite.
    try:
        authenticated_user = JupyterTicketStore().redeem(ticket)
    except Exception as exception:
        current_app.logger.exception(
            "Could not redeem a JupyterHub SSO ticket: %s",
            type(exception).__name__,
        )
        return jsonify({"error": "Authentication service unavailable"}), 503

    if authenticated_user is None:
        return jsonify({"error": "Invalid or expired ticket"}), 401

    return jsonify({
        "authenticated": True,
        "user": authenticated_user,
    }), 200
