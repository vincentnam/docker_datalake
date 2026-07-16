# datalake_sso.py - Keycloak SSO (OIDC Authorization Code) Backend-for-Frontend.
#
# Flow (BFF : the OIDC client secret never reaches the browser) :
#   1. GET /auth/config   -> login options : one entry per identity provider
#      registered in Keystone (listed with the idp-reader service account).
#   2. GET /auth/login?idp=<id> -> redirect the browser to that IdP's login page.
#   3. Keycloak redirects back to GET /auth/callback?code=...&state=...
#   4. Flask exchanges the code directly (keeping the id_token for logout),
#      trades the access token for a federated Keystone token (v3oidcaccesstoken),
#      then redirects the browser to the registered client. The web GUI receives
#      its scoped Keystone token; JupyterHub receives a short-lived one-time
#      ticket that it redeems server-to-server through Flask.
#
# The web GUI keeps using a *Keystone* token as Bearer, exactly like the
# username/password login : SSO is just another way to obtain that token.

import os
import secrets
import time
from urllib.parse import urlencode

import requests
from flask import Blueprint, request, redirect, session, jsonify, current_app

from keystoneauth1 import session as ksa_session
from keystoneauth1.identity.v3 import OidcAccessToken, Token

from datalake_jupyter_auth import issue_jupyter_ticket


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
        "jupyterhub_login_url": os.getenv(
            "JUPYTERHUB_PUBLIC_LOGIN_URL",
            "http://localhost:7000/hub/hub/login",
        ),
        # Read-only service account used to list the IdPs registered in
        # Keystone (drives the dynamic login buttons of the web GUI).
        "idp_reader_user": os.getenv("IDP_READER_USER", ""),
        "idp_reader_password": os.getenv("IDP_READER_PASSWORD", ""),
        "idp_reader_project": os.getenv("IDP_READER_PROJECT", "service"),
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


# Cache of the identity providers registered in Keystone : the login page
# requests them on every load, no need to hammer Keystone.
_IDP_CACHE = {"fetched_at": 0.0, "idps": None}
_IDP_CACHE_TTL = 60  # seconds


def _idp_client_cfg(idp_id):
    """OIDC client (relying party) configuration for one identity provider.

    Single-IdP for now : only the statically configured Keycloak has client
    credentials. To plug another IdP later, return here a dict with the same
    shape as _cfg() (its own kc_public_url / kc_internal_url / realm / client
    id / secret), keyed on its Keystone IdP id. Returns None for an unknown
    IdP so callers can reject it.
    """
    c = _cfg()
    if idp_id == c["idp"]:
        return c
    return None


def _keystone_service_token(c):
    """Token of the read-only idp-reader service account (None if unset)."""
    if not (c["idp_reader_user"] and c["idp_reader_password"]):
        return None
    body = {
        "auth": {
            "identity": {
                "methods": ["password"],
                "password": {
                    "user": {
                        "name": c["idp_reader_user"],
                        "domain": {"name": "Default"},
                        "password": c["idp_reader_password"],
                    }
                },
            },
            "scope": {
                "project": {
                    "name": c["idp_reader_project"],
                    "domain": {"name": "Default"},
                }
            },
        }
    }
    resp = requests.post(
        f"{c['keystone_url'].rstrip('/')}/auth/tokens", json=body, timeout=10
    )
    resp.raise_for_status()
    return resp.headers["X-Subject-Token"]


def _list_idps(c):
    """Identity providers registered in Keystone (id + description).

    Keystone is the source of truth : an IdP registered by the bootstrap shows
    up on the login page automatically. Only IdPs the BFF has OIDC client
    credentials for are kept (an entry without a secret would just be a broken
    button). Falls back to the statically configured IdP when Keystone can't
    be queried, so the login page keeps working.
    """
    now = time.time()
    if _IDP_CACHE["idps"] is not None and now - _IDP_CACHE["fetched_at"] < _IDP_CACHE_TTL:
        return _IDP_CACHE["idps"]

    idps = None
    try:
        token = _keystone_service_token(c)
        if token:
            resp = requests.get(
                f"{c['keystone_url'].rstrip('/')}/OS-FEDERATION/identity_providers",
                headers={"X-Auth-Token": token},
                timeout=10,
            )
            resp.raise_for_status()
            idps = [
                {"id": idp["id"], "description": idp.get("description")}
                for idp in resp.json().get("identity_providers", [])
                if idp.get("enabled", True)
            ]
    except Exception:
        current_app.logger.exception("Could not list identity providers from Keystone")

    if idps is None:
        # Legacy deployments without an IdP reader keep the static fallback.
        # When the reader is configured, a lookup failure means the federation
        # bootstrap is unhealthy and must not produce a broken login button.
        if c["idp_reader_user"] and c["idp_reader_password"]:
            idps = []
        else:
            idps = [{"id": c["idp"], "description": None}]

    idps = [i for i in idps if _idp_client_cfg(i["id"]) is not None]

    _IDP_CACHE.update({"fetched_at": now, "idps": idps})
    return idps


def _authorize_endpoint(c):
    return f"{c['kc_public_url']}/realms/{c['realm']}/protocol/openid-connect/auth"


def _token_endpoint(c):
    # Internal URL : Flask <-> Keycloak is server-to-server.
    base = c["kc_internal_url"] or c["kc_public_url"]
    return f"{base}/realms/{c['realm']}/protocol/openid-connect/token"


def _end_session_endpoint(c):
    # Public URL : the browser is navigated there so Keycloak can clear its
    # SSO session cookie (RP-initiated logout).
    return f"{c['kc_public_url']}/realms/{c['realm']}/protocol/openid-connect/logout"


def _gui_redirect(c, fragment):
    return redirect(f"{c['web_gui_url']}/#{fragment}")


def _safe_jupyter_next(value):
    """Only accept paths inside the public JupyterHub prefix."""
    if isinstance(value, str) and value.startswith("/hub/") and not value.startswith("//"):
        return value
    return "/hub/"


def _client_redirect(c, client, next_path, fragment):
    if client == "jupyterhub":
        query = urlencode({"next": _safe_jupyter_next(next_path)})
        return redirect(f"{c['jupyterhub_login_url']}?{query}#{fragment}")
    return _gui_redirect(c, fragment)


@sso_bp.route("/auth/config", methods=["GET"])
def auth_config():
    """Login options for the web GUI : local login + one button per identity
    provider registered in Keystone."""
    if not sso_enabled():
        return jsonify({"sso_enabled": False, "idps": []}), 200

    c = _cfg()
    idps = [
        {
            "id": idp["id"],
            "description": idp.get("description"),
            "login_url": f"/api/auth/login?idp={idp['id']}",
        }
        for idp in _list_idps(c)
    ]
    return jsonify({"sso_enabled": bool(idps), "idps": idps}), 200


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

    # Keep the Flask session (it may hold the Keycloak id_token) : the GET
    # /auth/logout navigation right after this call needs it to close the
    # Keycloak SSO session, and clears everything itself.
    session.pop("oidc_state", None)
    return jsonify({"revoked": revoked}), 200


@sso_bp.route("/auth/logout", methods=["GET"])
def auth_logout_sso():
    """Browser-navigated logout : close the Keycloak SSO session, then land
    back on the GUI login page.

    Revoking the Keystone token (POST above) is not enough for a real logout :
    the Keycloak SSO cookie survives in the browser, so the next 'login with
    Keycloak' silently re-authenticates the same user and switching accounts is
    impossible. This endpoint is a full-page navigation so Keycloak can clear
    that cookie (RP-initiated logout ; id_token_hint skips the confirmation
    screen). Without an SSO session it just bounces back to the GUI.
    """
    id_token = session.pop("oidc_id_token", None)
    idp_id = session.pop("oidc_idp", None)
    session.clear()
    # End the session on the IdP the user actually logged in through.
    c = _idp_client_cfg(idp_id) if idp_id else None
    if c is None:
        c = _cfg()

    if sso_enabled() and id_token:
        params = {
            "id_token_hint": id_token,
            "client_id": c["client_id"],
            "post_logout_redirect_uri": c["web_gui_url"],
        }
        return redirect(f"{_end_session_endpoint(c)}?{urlencode(params)}")

    return redirect(c["web_gui_url"])


@sso_bp.route("/auth/login", methods=["GET"])
def auth_login():
    if not sso_enabled():
        return jsonify({"error": "SSO is not enabled"}), 404

    idp_id = request.args.get("idp") or _cfg()["idp"]
    c = _idp_client_cfg(idp_id)
    if c is None:
        return jsonify({"error": f"Unknown identity provider '{idp_id}'"}), 404

    client = request.args.get("client", "web_gui")
    if client not in {"web_gui", "jupyterhub"}:
        return jsonify({"error": f"Unknown authentication client '{client}'"}), 400

    state = secrets.token_urlsafe(24)
    session["oidc_state"] = state
    # Remember which IdP this login round-trip belongs to : the callback needs
    # its token endpoint / client credentials.
    session["oidc_login_idp"] = idp_id
    session["oidc_login_client"] = client
    session["oidc_login_next"] = (
        _safe_jupyter_next(request.args.get("next")) if client == "jupyterhub" else ""
    )

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
    if not sso_enabled():
        return jsonify({"error": "SSO is not enabled"}), 404

    # The login round-trip was started for a specific IdP (see auth_login).
    idp_id = session.pop("oidc_login_idp", None) or _cfg()["idp"]
    client = session.pop("oidc_login_client", "web_gui")
    next_path = session.pop("oidc_login_next", "")
    c = _idp_client_cfg(idp_id)
    if c is None:
        c = _cfg()
        return _client_redirect(
            c,
            client,
            next_path,
            urlencode({"sso_error": f"Unknown identity provider '{idp_id}'"}),
        )

    error = request.args.get("error")
    if error:
        return _client_redirect(
            c,
            client,
            next_path,
            urlencode({"sso_error": request.args.get("error_description", error)}),
        )

    code = request.args.get("code")
    state = request.args.get("state")
    expected_state = session.pop("oidc_state", None)
    if not code or not state or state != expected_state:
        return _client_redirect(
            c,
            client,
            next_path,
            urlencode({"sso_error": "Invalid SSO state or missing code"}),
        )

    try:
        # Exchange the authorization code against Keycloak DIRECTLY (instead of
        # letting keystoneauth do it) : we need the id_token too, kept in the
        # Flask session to close the Keycloak SSO session on logout
        # (id_token_hint of the RP-initiated logout).
        tk_resp = requests.post(
            _token_endpoint(c),
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": c["redirect_uri"],
                "client_id": c["client_id"],
                "client_secret": c["client_secret"],
            },
            timeout=10,
        )
        tk_resp.raise_for_status()
        kc_tokens = tk_resp.json()
        session["oidc_id_token"] = kc_tokens.get("id_token")
        # Kept for the logout : the end-session endpoint is per-IdP.
        session["oidc_idp"] = idp_id

        # Trade the Keycloak access token for a *federated unscoped* Keystone
        # token.
        auth = OidcAccessToken(
            auth_url=c["keystone_url"],
            identity_provider=idp_id,
            protocol=c["protocol"],
            access_token=kc_tokens["access_token"],
        )
        sess = ksa_session.Session(auth=auth)
        unscoped_token = sess.get_token()
        access_info = auth.auth_ref

        # List the projects the federated user can access, pick one, scope.
        projects = _list_projects(c["keystone_url"], unscoped_token)
        if not projects:
            return _client_redirect(
                c,
                client,
                next_path,
                urlencode({"sso_error": "No project available for this user"}),
            )

        if client == "jupyterhub":
            if not access_info.user_id or not access_info.username:
                raise RuntimeError("Keystone did not return a federated user identity")
            ticket = issue_jupyter_ticket(access_info.user_id, access_info.username)
            try:
                requests.delete(
                    f"{c['keystone_url'].rstrip('/')}/auth/tokens",
                    headers={
                        "X-Auth-Token": unscoped_token,
                        "X-Subject-Token": unscoped_token,
                    },
                    timeout=10,
                )
            except Exception:
                current_app.logger.warning(
                    "Could not revoke the temporary JupyterHub Keystone token"
                )
            return _client_redirect(
                c,
                client,
                next_path,
                urlencode({"flask_ticket": ticket}),
            )

        project = _pick_project(projects, c["preferred_project"])
        scope_auth = Token(
            auth_url=c["keystone_url"],
            token=unscoped_token,
            project_id=project["id"],
        )
        scoped_token = ksa_session.Session(auth=scope_auth).get_token()

        return _gui_redirect(
            c, urlencode({
                "sso_token": scoped_token,
                "project": project["name"],
                # Domain-agnostic reference : the GUI sends it back as the
                # Project-Id header (federated projects don't live in Default).
                "project_id": project["id"],
            })
        )

    except Exception as exc:  # noqa: BLE001 - surface a readable error to the GUI
        current_app.logger.exception("SSO callback failed")
        return _client_redirect(
            c,
            client,
            next_path,
            urlencode({"sso_error": str(exc)}),
        )


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
