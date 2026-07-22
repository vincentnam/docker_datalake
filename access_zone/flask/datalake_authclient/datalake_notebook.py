"""Création et authentification des notebooks du lac de données."""

import hashlib
import html
import os
import secrets
import sqlite3
import time
from contextlib import closing
from urllib.parse import urlencode

from flask import Blueprint, Response, jsonify, request


notebook_blueprint = Blueprint("datalake_notebook", __name__)


class NotebookAuthenticationStore:
    """Stocke brièvement le résultat d'une connexion SSO destinée à un kernel."""

    DEFAULT_DATABASE = "/tmp/datalake-jupyter-sso.sqlite3"
    DEFAULT_VALIDITY_SECONDS = 300

    def __init__(self, database_path=None):
        self.database_path = database_path or os.getenv(
            "JUPYTER_SSO_TICKET_DB",
            self.DEFAULT_DATABASE,
        )

    def _connect(self):
        connection = sqlite3.connect(self.database_path, timeout=5)
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS notebook_authentication_requests (
                request_id TEXT PRIMARY KEY,
                polling_secret_digest TEXT NOT NULL,
                status TEXT NOT NULL,
                access_token TEXT,
                project_name TEXT,
                project_id TEXT,
                error_message TEXT,
                expires_at INTEGER NOT NULL
            )
            """
        )
        return connection

    @staticmethod
    def _hash_secret(polling_secret):
        return hashlib.sha256(polling_secret.encode("utf-8")).hexdigest()

    def create(self):
        request_id = secrets.token_urlsafe(24)
        polling_secret = secrets.token_urlsafe(32)
        current_timestamp = int(time.time())

        with closing(self._connect()) as connection:
            connection.execute(
                "DELETE FROM notebook_authentication_requests WHERE expires_at < ?",
                (current_timestamp,),
            )
            connection.execute(
                """
                INSERT INTO notebook_authentication_requests
                    (request_id, polling_secret_digest, status, expires_at)
                VALUES (?, ?, 'pending', ?)
                """,
                (
                    request_id,
                    self._hash_secret(polling_secret),
                    current_timestamp + self.DEFAULT_VALIDITY_SECONDS,
                ),
            )
            connection.commit()

        return request_id, polling_secret

    def exists(self, request_id):
        current_timestamp = int(time.time())
        with closing(self._connect()) as connection:
            authentication_request = connection.execute(
                """
                SELECT 1
                FROM notebook_authentication_requests
                WHERE request_id = ? AND expires_at >= ?
                """,
                (request_id, current_timestamp),
            ).fetchone()
        return authentication_request is not None

    def complete(self, request_id, access_token, project_name, project_id):
        with closing(self._connect()) as connection:
            connection.execute(
                """
                UPDATE notebook_authentication_requests
                SET status = 'complete', access_token = ?, project_name = ?,
                    project_id = ?, error_message = NULL
                WHERE request_id = ? AND expires_at >= ?
                """,
                (
                    access_token,
                    project_name,
                    project_id,
                    request_id,
                    int(time.time()),
                ),
            )
            connection.commit()

    def fail(self, request_id, error_message):
        if not request_id:
            return
        with closing(self._connect()) as connection:
            connection.execute(
                """
                UPDATE notebook_authentication_requests
                SET status = 'error', error_message = ?
                WHERE request_id = ? AND expires_at >= ?
                """,
                (error_message, request_id, int(time.time())),
            )
            connection.commit()

    def poll(self, request_id, polling_secret):
        current_timestamp = int(time.time())
        polling_secret_digest = self._hash_secret(polling_secret)
        connection = self._connect()

        try:
            connection.execute("BEGIN IMMEDIATE")
            authentication_request = connection.execute(
                """
                SELECT status, access_token, project_name, project_id,
                       error_message, expires_at
                FROM notebook_authentication_requests
                WHERE request_id = ? AND polling_secret_digest = ?
                """,
                (request_id, polling_secret_digest),
            ).fetchone()

            if authentication_request is None:
                connection.rollback()
                return None

            (
                status,
                access_token,
                project_name,
                project_id,
                error_message,
                expires_at,
            ) = authentication_request
            if expires_at < current_timestamp:
                connection.execute(
                    "DELETE FROM notebook_authentication_requests WHERE request_id = ?",
                    (request_id,),
                )
                connection.commit()
                return None

            # Le token n'est délivré qu'une fois au kernel qui possède le secret.
            if status in {"complete", "error"}:
                connection.execute(
                    "DELETE FROM notebook_authentication_requests WHERE request_id = ?",
                    (request_id,),
                )
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

        return {
            "status": status,
            "access_token": access_token,
            "project_name": project_name,
            "project_id": project_id,
            "error": error_message,
        }


@notebook_blueprint.route("/auth/notebook/sso/start", methods=["POST"])
def start_notebook_sso():
    request_payload = request.get_json(silent=True) or {}
    identity_provider = request_payload.get("identity_provider")
    if (
        not isinstance(identity_provider, str)
        or not identity_provider.strip()
        or len(identity_provider) > 255
    ):
        return jsonify({"error": "Invalid identity provider"}), 400

    request_id, polling_secret = NotebookAuthenticationStore().create()
    public_web_gui_url = os.getenv(
        "WEB_GUI_URL",
        "http://localhost:7000",
    ).rstrip("/")
    public_flask_url = f"{public_web_gui_url}/api"
    query_parameters = urlencode({
        "client": "notebook",
        "idp": identity_provider.strip(),
        "request_id": request_id,
    })
    return jsonify({
        "request_id": request_id,
        "polling_secret": polling_secret,
        "login_url": f"{public_flask_url}/auth/login?{query_parameters}",
    }), 201


@notebook_blueprint.route("/auth/notebook/sso/status", methods=["POST"])
def get_notebook_sso_status():
    request_payload = request.get_json(silent=True) or {}
    request_id = request_payload.get("request_id")
    polling_secret = request_payload.get("polling_secret")
    if (
        not isinstance(request_id, str)
        or not isinstance(polling_secret, str)
        or len(request_id) > 255
        or len(polling_secret) > 512
    ):
        return jsonify({"error": "Invalid authentication request"}), 400

    authentication_status = NotebookAuthenticationStore().poll(
        request_id,
        polling_secret,
    )
    if authentication_status is None:
        return jsonify({"error": "Invalid or expired authentication request"}), 404
    return jsonify(authentication_status), 200


@notebook_blueprint.route("/auth/notebook/result", methods=["GET"])
def show_notebook_sso_result():
    error_message = request.args.get("sso_error")
    if error_message:
        return Response(
            f"<h1>Connexion refusée</h1><p>{html.escape(error_message)}</p>",
            status=400,
            content_type="text/html; charset=utf-8",
        )
    return Response(
        "<h1>Connexion terminée</h1><p>Vous pouvez revenir au notebook.</p>",
        content_type="text/html; charset=utf-8",
    )
