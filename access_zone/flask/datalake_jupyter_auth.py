"""Authentication endpoints used by JupyterHub.

Local Keystone credentials and federated one-time tickets are supported.
"""

import hashlib
import os
import secrets
import sqlite3
import time

from flask import Blueprint, current_app, jsonify, request
from keystoneauth1 import session as keystone_session
from keystoneauth1.exceptions import ClientException
from keystoneauth1.exceptions.http import Unauthorized
from keystoneauth1.identity import v3


jupyter_auth_bp = Blueprint("jupyter_auth", __name__)


def _ticket_database_path():
    return os.getenv("JUPYTER_SSO_TICKET_DB", "/tmp/datalake-jupyter-sso.sqlite3")


def _ticket_ttl():
    try:
        return max(10, min(int(os.getenv("JUPYTER_SSO_TICKET_TTL", "60")), 300))
    except ValueError:
        return 60


def _ticket_digest(ticket):
    return hashlib.sha256(ticket.encode("utf-8")).hexdigest()


def _ticket_database():
    connection = sqlite3.connect(_ticket_database_path(), timeout=5)
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


def issue_jupyter_ticket(user_id, username):
    """Create a short-lived opaque ticket shared by all Gunicorn workers."""
    ticket = secrets.token_urlsafe(32)
    now = int(time.time())

    with _ticket_database() as connection:
        connection.execute(
            "DELETE FROM jupyter_sso_tickets WHERE expires_at < ?",
            (now,),
        )
        connection.execute(
            """
            INSERT INTO jupyter_sso_tickets (digest, user_id, username, expires_at)
            VALUES (?, ?, ?, ?)
            """,
            (_ticket_digest(ticket), user_id, username, now + _ticket_ttl()),
        )

    return ticket


def _redeem_jupyter_ticket(ticket):
    """Atomically consume a ticket so it cannot be replayed."""
    now = int(time.time())
    digest = _ticket_digest(ticket)
    connection = _ticket_database()

    try:
        connection.execute("BEGIN IMMEDIATE")
        row = connection.execute(
            """
            SELECT user_id, username, expires_at
            FROM jupyter_sso_tickets
            WHERE digest = ?
            """,
            (digest,),
        ).fetchone()
        connection.execute(
            "DELETE FROM jupyter_sso_tickets WHERE digest = ? OR expires_at < ?",
            (digest, now),
        )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()

    if row is None or row[2] < now:
        return None
    return {"id": row[0], "username": row[1], "source": "keystone_sso"}


def _keystone_url():
    return os.getenv("KEYSTONE_URL", "http://keystone:5000/v3")


@jupyter_auth_bp.route("/auth/jupyter/local", methods=["POST"])
def jupyter_local_login():
    """Validate a local Keystone account without exposing its token.

    JupyterHub sends the credentials over the internal Docker network. Flask
    authenticates them against Keystone and returns only the stable identity
    required to create a JupyterHub session.
    """
    payload = request.get_json(silent=True) or {}
    username = payload.get("username")
    password = payload.get("password")

    if not isinstance(username, str) or not username.strip():
        return jsonify({"error": "Invalid credentials"}), 401
    if not isinstance(password, str) or not password:
        return jsonify({"error": "Invalid credentials"}), 401
    if len(username) > 255 or len(password) > 4096:
        return jsonify({"error": "Invalid credentials"}), 401

    username = username.strip()

    try:
        auth = v3.Password(
            auth_url=_keystone_url(),
            username=username,
            password=password,
            user_domain_name="Default",
        )
        session = keystone_session.Session(auth=auth, connect_retries=1)
        access = auth.get_access(session)

        return jsonify({
            "authenticated": True,
            "user": {
                "id": access.user_id,
                "username": access.username,
                "source": "keystone_local",
            },
        }), 200
    except Unauthorized:
        return jsonify({"error": "Invalid credentials"}), 401
    except ClientException as exc:
        current_app.logger.warning(
            "JupyterHub local authentication failed for user %s: %s",
            username,
            type(exc).__name__,
        )
        return jsonify({"error": "Authentication service unavailable"}), 503
    except Exception as exc:
        current_app.logger.exception(
            "Unexpected JupyterHub authentication error for user %s: %s",
            username,
            type(exc).__name__,
        )
        return jsonify({"error": "Authentication service unavailable"}), 503


@jupyter_auth_bp.route("/auth/jupyter/ticket", methods=["POST"])
def jupyter_ticket_login():
    """Redeem the one-time ticket created by the federated SSO callback."""
    payload = request.get_json(silent=True) or {}
    ticket = payload.get("ticket")

    if not isinstance(ticket, str) or not ticket or len(ticket) > 512:
        return jsonify({"error": "Invalid or expired ticket"}), 401

    try:
        user = _redeem_jupyter_ticket(ticket)
    except Exception as exc:
        current_app.logger.exception(
            "Could not redeem a JupyterHub SSO ticket: %s",
            type(exc).__name__,
        )
        return jsonify({"error": "Authentication service unavailable"}), 503

    if user is None:
        return jsonify({"error": "Invalid or expired ticket"}), 401

    return jsonify({"authenticated": True, "user": user}), 200
