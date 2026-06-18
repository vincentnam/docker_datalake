# datalake_sso.py - Keycloak SSO (OIDC Authorization Code) Backend-for-Frontend.
#
# Flow (BFF : the OIDC client secret never reaches the browser) :
#   1. GET /auth/login    -> redirect the browser to the Keycloak login page.
#   2. Keycloak redirects back to GET /auth/callback?code=...&state=...
#   3. Flask exchanges the code for a Keycloak access token AND a federated
#      Keystone token in one step (keystoneauth v3oidcauthcode), scopes it to a
#      project, then redirects the browser back to the web GUI with the Keystone
#      token in the URL fragment. The GUI finalizes via the existing Bearer flow.
#
# The web GUI keeps using a *Keystone* token as Bearer, exactly like the
# username/password login : SSO is just another way to obtain that token.

import os
import secrets
from urllib.parse import urlencode

import requests
from flask import Blueprint, request, redirect, session, jsonify, current_app

from keystoneauth1 import session as ksa_session
from keystoneauth1.identity.v3 import OidcAuthorizationCode, Token


sso_bp = Blueprint("sso", __name__)


def _cfg():
    """Read the SSO configuration from the environment (loaded from .env)."""
    return {
        "enabled": os.getenv("FEDERATION_ENABLED", "false").lower() == "true",
        "keystone_url": os.getenv("KEYSTONE_URL", "http://keystone:5000/v3"),
        "kc_public_url": os.getenv("KEYCLOAK_PUBLIC_URL", "").rstrip("/"),
        "kc_internal_url": os.getenv("KEYCLOAK_URL", "").rstrip("/"),
        "realm": os.getenv("KEYCLOAK_REALM", ""),
        "client_id": os.getenv("KEYCLOAK_CLIENT_ID", ""),
        "client_secret": os.getenv("KEYCLOAK_CLIENT_SECRET", ""),
        "redirect_uri": os.getenv("KEYCLOAK_REDIRECT_URI", ""),
        "idp": os.getenv("KEYCLOAK_IDP_ID", "keycloak"),
        "protocol": os.getenv("KEYCLOAK_PROTOCOL_ID", "openid"),
        "preferred_project": os.getenv("FEDERATED_PROJECT", ""),
        "web_gui_url": os.getenv("WEB_GUI_URL", "http://localhost:7000").rstrip("/"),
    }


def sso_enabled():
    c = _cfg()
    return bool(
        c["enabled"]
        and c["kc_public_url"]
        and c["realm"]
        and c["client_id"]
        and c["redirect_uri"]
    )


def _authorize_endpoint(c):
    return f"{c['kc_public_url']}/realms/{c['realm']}/protocol/openid-connect/auth"


def _token_endpoint(c):
    # Internal URL : Flask <-> Keycloak is server-to-server.
    base = c["kc_internal_url"] or c["kc_public_url"]
    return f"{base}/realms/{c['realm']}/protocol/openid-connect/token"


def _gui_redirect(c, fragment):
    return redirect(f"{c['web_gui_url']}/#{fragment}")


@sso_bp.route("/auth/config", methods=["GET"])
def auth_config():
    """Let the web GUI know whether to show the 'Login with Keycloak' button."""
    return jsonify({"sso_enabled": sso_enabled(), "login_url": "/api/auth/login"}), 200


@sso_bp.route("/auth/logout", methods=["POST"])
def auth_logout():
    """Log the user out by REVOKING their Keystone token server-side.

    Clearing the browser storage alone leaves the token valid until it expires :
    anyone who captured it could keep using it. Here we ask Keystone to revoke
    it immediately (DELETE /v3/auth/tokens, the token authorizes its own
    revocation), so it can no longer be used by anyone.
    """
    c = _cfg()

    auth_header = request.headers.get("Authorization", "")
    token = None
    if auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1].strip()
    if not token:
        token = request.headers.get("X-Subject-Token")

    revoked = False
    if token:
        try:
            resp = requests.delete(
                f"{c['keystone_url'].rstrip('/')}/auth/tokens",
                headers={"X-Auth-Token": token, "X-Subject-Token": token},
                timeout=10,
            )
            revoked = resp.status_code in (200, 204)
            if not revoked:
                current_app.logger.warning(
                    f"Token revocation returned HTTP {resp.status_code}"
                )
        except Exception:
            current_app.logger.exception("Token revocation failed")

    # Drop any server-side SSO session/state cookie too.
    session.clear()
    return jsonify({"revoked": revoked}), 200


@sso_bp.route("/auth/login", methods=["GET"])
def auth_login():
    c = _cfg()
    if not sso_enabled():
        return jsonify({"error": "SSO is not enabled"}), 404

    state = secrets.token_urlsafe(24)
    session["oidc_state"] = state

    params = {
        "client_id": c["client_id"],
        "response_type": "code",
        "scope": "openid email profile",
        "redirect_uri": c["redirect_uri"],
        "state": state,
    }
    return redirect(f"{_authorize_endpoint(c)}?{urlencode(params)}")


@sso_bp.route("/auth/callback", methods=["GET"])
def auth_callback():
    c = _cfg()
    if not sso_enabled():
        return jsonify({"error": "SSO is not enabled"}), 404

    error = request.args.get("error")
    if error:
        return _gui_redirect(c, urlencode({"sso_error": request.args.get("error_description", error)}))

    code = request.args.get("code")
    state = request.args.get("state")
    expected_state = session.pop("oidc_state", None)
    if not code or not state or state != expected_state:
        return _gui_redirect(c, urlencode({"sso_error": "Invalid SSO state or missing code"}))

    try:
        # Exchange the authorization code for a *federated unscoped* Keystone
        # token (keystoneauth does code -> Keycloak access token -> Keystone).
        auth = OidcAuthorizationCode(
            auth_url=c["keystone_url"],
            identity_provider=c["idp"],
            protocol=c["protocol"],
            client_id=c["client_id"],
            client_secret=c["client_secret"],
            access_token_endpoint=_token_endpoint(c),
            redirect_uri=c["redirect_uri"],
            code=code,
        )
        sess = ksa_session.Session(auth=auth)
        unscoped_token = sess.get_token()

        # List the projects the federated user can access, pick one, scope.
        projects = _list_projects(c["keystone_url"], unscoped_token)
        if not projects:
            return _gui_redirect(c, urlencode({"sso_error": "No project available for this user"}))

        project = _pick_project(projects, c["preferred_project"])
        scope_auth = Token(
            auth_url=c["keystone_url"],
            token=unscoped_token,
            project_id=project["id"],
        )
        scoped_token = ksa_session.Session(auth=scope_auth).get_token()

        return _gui_redirect(
            c, urlencode({"sso_token": scoped_token, "project": project["name"]})
        )

    except Exception as exc:  # noqa: BLE001 - surface a readable error to the GUI
        current_app.logger.exception("SSO callback failed")
        return _gui_redirect(c, urlencode({"sso_error": str(exc)}))


def _list_projects(keystone_url, unscoped_token):
    resp = requests.get(
        f"{keystone_url.rstrip('/')}/auth/projects",
        headers={"X-Auth-Token": unscoped_token},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json().get("projects", [])


def _pick_project(projects, preferred_name):
    if preferred_name:
        for p in projects:
            if p.get("name") == preferred_name:
                return p
    return projects[0]
