"""Gestion du flux SSO entre Keycloak, Keystone et les clients Flask.

Flask conserve le secret du client OpenID Connect et orchestre le flux :

1. le navigateur est redirigé vers l'Identity Provider par Keycloak ;
2. Flask échange le code d'autorisation contre les tokens Keycloak ;
3. le token Keycloak est échangé contre un token Keystone fédéré ;
4. l'utilisateur est renvoyé vers la Web GUI ou JupyterHub.

La Web GUI reçoit un token Keystone. JupyterHub reçoit uniquement un ticket
temporaire à usage unique qu'il échange ensuite auprès de Flask.
"""

import os
import secrets
import time
from urllib.parse import parse_qs, urlencode

import requests
from flask import Blueprint, current_app, jsonify, redirect, request, session
from keystoneauth1 import session as keystone_authentication_session
from keystoneauth1.identity.v3 import OidcAccessToken, Token

from .datalake_jupyter_auth import JupyterTicketStore
from .datalake_notebook import NotebookAuthenticationStore


sso_blueprint = Blueprint("sso", __name__)

# Evite de redemander la liste à Keystone à chaque affichage du login.
_IDENTITY_PROVIDER_CACHE_DURATION_SECONDS = 60
_identity_provider_cache = {
    "fetched_at": 0.0,
    "identity_providers": None,
}


def _get_sso_configuration():
    """Retourne la configuration SSO chargée depuis l'environnement."""
    return {
        "enabled": os.getenv("FEDERATION_ENABLED", "false").lower() == "true",
        "keystone_url": os.getenv("KEYSTONE_URL", "http://keystone:5000/v3"),
        "keycloak_public_url": os.getenv("KEYCLOAK_PUBLIC_URL", "").rstrip("/"),
        "keycloak_internal_url": os.getenv("KEYCLOAK_URL", "").rstrip("/"),
        "keycloak_realm": os.getenv("KEYCLOAK_REALM", ""),
        "keycloak_client_id": os.getenv("KEYCLOAK_CLIENT_ID", ""),
        "keycloak_client_secret": os.getenv("KEYCLOAK_CLIENT_SECRET", ""),
        "keycloak_redirect_uri": os.getenv("KEYCLOAK_REDIRECT_URI", ""),
        "identity_provider_id": os.getenv("KEYCLOAK_IDP_ID", "keycloak"),
        "federation_protocol": os.getenv("KEYCLOAK_PROTOCOL_ID", "openid"),
        "preferred_project_name": os.getenv("FEDERATED_PROJECT", ""),
        "web_gui_url": os.getenv(
            "WEB_GUI_URL",
            "http://localhost:7000",
        ).rstrip("/"),
        "jupyterhub_login_url": os.getenv(
            "JUPYTERHUB_PUBLIC_LOGIN_URL",
            "http://localhost:7000/hub/hub/login",
        ),
        "identity_provider_reader_username": os.getenv("IDP_READER_USER", ""),
        "identity_provider_reader_password": os.getenv("IDP_READER_PASSWORD", ""),
        "identity_provider_reader_project": os.getenv(
            "IDP_READER_PROJECT",
            "service",
        ),
    }


def is_sso_enabled(configuration=None):
    """Vérifie que les paramètres indispensables au SSO sont présents."""
    configuration = configuration or _get_sso_configuration()
    return bool(
        configuration["enabled"]
        and configuration["keycloak_public_url"]
        and configuration["keycloak_realm"]
        and configuration["keycloak_client_id"]
        and configuration["keycloak_redirect_uri"]
    )


def _get_identity_provider_configuration(identity_provider_id):
    """Retourne la configuration du client associé à un Identity Provider.

    Un seul Identity Provider est configuré pour le moment. Cette fonction est
    le point d'extension pour associer plus tard chaque Identity Provider à son
    propre client OpenID Connect.
    """
    # Pour l'instant on a un seul client Keycloak. Plus tard on pourra retourner
    # une configuration différente pour chaque Identity Provider.
    configuration = _get_sso_configuration()
    if identity_provider_id == configuration["identity_provider_id"]:
        return configuration
    return None


def _get_keystone_service_token(configuration):
    """Crée le token du compte de service qui consulte les Identity Providers."""
    reader_username = configuration["identity_provider_reader_username"]
    reader_password = configuration["identity_provider_reader_password"]
    if not (reader_username and reader_password):
        return None

    authentication_payload = {
        "auth": {
            "identity": {
                "methods": ["password"],
                "password": {
                    "user": {
                        "name": reader_username,
                        "domain": {"name": "Default"},
                        "password": reader_password,
                    }
                },
            },
            "scope": {
                "project": {
                    "name": configuration["identity_provider_reader_project"],
                    "domain": {"name": "Default"},
                }
            },
        }
    }
    keystone_response = requests.post(
        f"{configuration['keystone_url'].rstrip('/')}/auth/tokens",
        json=authentication_payload,
        timeout=10,
    )
    keystone_response.raise_for_status()
    return keystone_response.headers["X-Subject-Token"]


def _get_identity_provider_fallback(configuration):
    # Si le reader est configuré, Keystone doit rester la source de vérité.
    # Sans reader, on garde le fonctionnement des déploiements non fédérés.
    reader_is_configured = bool(
        configuration["identity_provider_reader_username"]
        and configuration["identity_provider_reader_password"]
    )
    if reader_is_configured:
        return []
    return [{
        "id": configuration["identity_provider_id"],
        "description": None,
    }]


def _list_identity_providers(configuration):
    """Liste les Identity Providers utilisables enregistrés dans Keystone."""
    current_time = time.time()
    cached_identity_providers = _identity_provider_cache["identity_providers"]
    cache_age = current_time - _identity_provider_cache["fetched_at"]

    if (
        cached_identity_providers is not None
        and cache_age < _IDENTITY_PROVIDER_CACHE_DURATION_SECONDS
    ):
        return cached_identity_providers

    identity_providers = None
    try:
        # Le compte reader a uniquement besoin de lire la configuration de
        # fédération, on ne réutilise jamais son token pour connecter un user.
        service_token = _get_keystone_service_token(configuration)
        if service_token:
            keystone_response = requests.get(
                (
                    f"{configuration['keystone_url'].rstrip('/')}"
                    "/OS-FEDERATION/identity_providers"
                ),
                headers={"X-Auth-Token": service_token},
                timeout=10,
            )
            keystone_response.raise_for_status()
            identity_providers = [
                {
                    "id": identity_provider["id"],
                    "description": identity_provider.get("description"),
                }
                for identity_provider in keystone_response.json().get(
                    "identity_providers",
                    [],
                )
                if identity_provider.get("enabled", True)
            ]
    except Exception:
        current_app.logger.exception(
            "Could not list identity providers from Keystone"
        )

    if identity_providers is None:
        identity_providers = _get_identity_provider_fallback(configuration)

    identity_providers = [
        identity_provider
        for identity_provider in identity_providers
        if _get_identity_provider_configuration(identity_provider["id"])
        is not None
    ]

    _identity_provider_cache.update({
        "fetched_at": current_time,
        "identity_providers": identity_providers,
    })
    return identity_providers


def _get_keycloak_authorization_endpoint(configuration):
    # URL publique : cette redirection est suivie par le navigateur.
    return (
        f"{configuration['keycloak_public_url']}"
        f"/realms/{configuration['keycloak_realm']}"
        "/protocol/openid-connect/auth"
    )


def _get_keycloak_token_endpoint(configuration):
    # URL interne : cet appel est fait directement de Flask vers Keycloak.
    keycloak_url = (
        configuration["keycloak_internal_url"]
        or configuration["keycloak_public_url"]
    )
    return (
        f"{keycloak_url}/realms/{configuration['keycloak_realm']}"
        "/protocol/openid-connect/token"
    )


def _get_keycloak_logout_endpoint(configuration):
    # URL publique : Keycloak doit supprimer son cookie dans le navigateur.
    return (
        f"{configuration['keycloak_public_url']}"
        f"/realms/{configuration['keycloak_realm']}"
        "/protocol/openid-connect/logout"
    )


def _get_safe_jupyterhub_next_path(requested_path):
    """Accepte uniquement une redirection interne au préfixe JupyterHub."""
    # On refuse une URL complète pour ne pas créer de redirection ouverte.
    if (
        isinstance(requested_path, str)
        and requested_path.startswith("/hub/")
        and not requested_path.startswith("//")
    ):
        return requested_path
    return "/hub/"


def _redirect_to_web_gui(configuration, url_fragment):
    return redirect(f"{configuration['web_gui_url']}/#{url_fragment}")


def _redirect_to_authentication_client(
    configuration,
    authentication_client,
    next_path,
    url_fragment,
):
    if authentication_client == "jupyterhub":
        query_parameters = urlencode({
            "next": _get_safe_jupyterhub_next_path(next_path),
        })
        return redirect(
            f"{configuration['jupyterhub_login_url']}"
            f"?{query_parameters}#{url_fragment}"
        )
    if authentication_client == "notebook":
        result_parameters = parse_qs(url_fragment)
        error_message = (result_parameters.get("sso_error") or [None])[0]
        if error_message:
            NotebookAuthenticationStore().fail(next_path, error_message)
        query_parameters = urlencode({"sso_error": error_message}) if error_message else ""
        result_url = f"{configuration['web_gui_url']}/api/auth/notebook/result"
        return redirect(f"{result_url}?{query_parameters}" if query_parameters else result_url)
    return _redirect_to_web_gui(configuration, url_fragment)


def _extract_keystone_token_from_request():
    authorization_header = request.headers.get("Authorization", "")
    if authorization_header.startswith("Bearer "):
        return authorization_header.split(" ", 1)[1].strip()
    return request.headers.get("X-Subject-Token")


def _revoke_keystone_token(configuration, keystone_token):
    if not keystone_token:
        return False

    # Le token peut autoriser sa propre révocation dans Keystone.
    keystone_response = requests.delete(
        f"{configuration['keystone_url'].rstrip('/')}/auth/tokens",
        headers={
            "X-Auth-Token": keystone_token,
            "X-Subject-Token": keystone_token,
        },
        timeout=10,
    )
    token_was_revoked = keystone_response.status_code in (200, 204)
    if not token_was_revoked:
        current_app.logger.warning(
            "Token revocation returned HTTP %s",
            keystone_response.status_code,
        )
    return token_was_revoked


def _exchange_authorization_code(configuration, authorization_code):
    """Échange le code d'autorisation contre les tokens Keycloak."""
    token_response = requests.post(
        _get_keycloak_token_endpoint(configuration),
        data={
            "grant_type": "authorization_code",
            "code": authorization_code,
            "redirect_uri": configuration["keycloak_redirect_uri"],
            "client_id": configuration["keycloak_client_id"],
            "client_secret": configuration["keycloak_client_secret"],
        },
        timeout=10,
    )
    token_response.raise_for_status()
    return token_response.json()


def _get_federated_keystone_identity(
    configuration,
    identity_provider_id,
    keycloak_access_token,
):
    """Échange le token Keycloak contre une identité Keystone non scopée."""
    # Keystone valide le token Keycloak via le mapping de fédération configuré.
    keystone_authentication = OidcAccessToken(
        auth_url=configuration["keystone_url"],
        identity_provider=identity_provider_id,
        protocol=configuration["federation_protocol"],
        access_token=keycloak_access_token,
    )
    keystone_session = keystone_authentication_session.Session(
        auth=keystone_authentication
    )
    unscoped_keystone_token = keystone_session.get_token()
    return unscoped_keystone_token, keystone_authentication.auth_ref


def _list_keystone_projects(keystone_url, unscoped_keystone_token):
    keystone_response = requests.get(
        f"{keystone_url.rstrip('/')}/auth/projects",
        headers={"X-Auth-Token": unscoped_keystone_token},
        timeout=10,
    )
    keystone_response.raise_for_status()
    return keystone_response.json().get("projects", [])


def _select_keystone_project(available_projects, preferred_project_name):
    if preferred_project_name:
        for available_project in available_projects:
            if available_project.get("name") == preferred_project_name:
                return available_project
    return available_projects[0]


@sso_blueprint.route("/auth/config", methods=["GET"])
def get_authentication_configuration():
    """Retourne les méthodes de connexion proposées aux clients Flask."""
    configuration = _get_sso_configuration()
    if not is_sso_enabled(configuration):
        return jsonify({"sso_enabled": False, "idps": []}), 200

    # Les noms de champs idp/idps sont gardés car ils font partie du contrat
    # actuel avec la Web GUI.
    identity_providers = [
        {
            "id": identity_provider["id"],
            "description": identity_provider.get("description"),
            "login_url": f"/api/auth/login?idp={identity_provider['id']}",
        }
        for identity_provider in _list_identity_providers(configuration)
    ]
    return jsonify({
        "sso_enabled": bool(identity_providers),
        "idps": identity_providers,
    }), 200


@sso_blueprint.route("/auth/logout", methods=["POST"])
def revoke_authentication_token():
    """Révoque immédiatement le token Keystone fourni par le client."""
    configuration = _get_sso_configuration()
    keystone_token = _extract_keystone_token_from_request()

    token_was_revoked = False
    try:
        token_was_revoked = _revoke_keystone_token(
            configuration,
            keystone_token,
        )
    except Exception:
        current_app.logger.exception("Token revocation failed")

    # On garde encore le token Keycloak en session : le GET logout qui suit en
    # a besoin pour fermer aussi la session SSO chez Keycloak.
    session.pop("oidc_state", None)
    return jsonify({"revoked": token_was_revoked}), 200


@sso_blueprint.route("/auth/logout", methods=["GET"])
def logout_sso_session():
    """Ferme la session Keycloak puis redirige vers la Web GUI."""
    keycloak_identity_token = session.pop("oidc_id_token", None)
    identity_provider_id = session.pop("oidc_idp", None)
    session.clear()

    # On ferme la session sur l'Identity Provider réellement utilisé au login.
    configuration = None
    if identity_provider_id:
        configuration = _get_identity_provider_configuration(identity_provider_id)
    configuration = configuration or _get_sso_configuration()

    if is_sso_enabled(configuration) and keycloak_identity_token:
        query_parameters = {
            "id_token_hint": keycloak_identity_token,
            "client_id": configuration["keycloak_client_id"],
            "post_logout_redirect_uri": configuration["web_gui_url"],
        }
        return redirect(
            f"{_get_keycloak_logout_endpoint(configuration)}"
            f"?{urlencode(query_parameters)}"
        )

    return redirect(configuration["web_gui_url"])


@sso_blueprint.route("/auth/login", methods=["GET"])
def start_sso_login():
    """Démarre le flux SSO pour la Web GUI ou JupyterHub."""
    default_configuration = _get_sso_configuration()
    if not is_sso_enabled(default_configuration):
        return jsonify({"error": "SSO is not enabled"}), 404

    identity_provider_id = (
        request.args.get("idp")
        or default_configuration["identity_provider_id"]
    )
    configuration = _get_identity_provider_configuration(identity_provider_id)
    if configuration is None:
        return jsonify({
            "error": f"Unknown identity provider '{identity_provider_id}'",
        }), 404

    authentication_client = request.args.get("client", "web_gui")
    if authentication_client not in {"web_gui", "jupyterhub", "notebook"}:
        return jsonify({
            "error": f"Unknown authentication client '{authentication_client}'",
        }), 400

    # Le state protège le callback et la session garde le client d'origine pour
    # savoir où renvoyer le user après la connexion.
    state_token = secrets.token_urlsafe(24)
    session["oidc_state"] = state_token
    session["oidc_login_idp"] = identity_provider_id
    session["oidc_login_client"] = authentication_client
    if authentication_client == "jupyterhub":
        next_path = _get_safe_jupyterhub_next_path(request.args.get("next"))
    elif authentication_client == "notebook":
        next_path = request.args.get("request_id", "")
        if not NotebookAuthenticationStore().exists(next_path):
            return jsonify({"error": "Invalid or expired notebook request"}), 400
    else:
        next_path = ""
    session["oidc_login_next"] = next_path

    query_parameters = {
        "client_id": configuration["keycloak_client_id"],
        "response_type": "code",
        "scope": "openid email profile",
        "redirect_uri": configuration["keycloak_redirect_uri"],
        "state": state_token,
    }
    return redirect(
        f"{_get_keycloak_authorization_endpoint(configuration)}"
        f"?{urlencode(query_parameters)}"
    )


@sso_blueprint.route("/auth/callback", methods=["GET"])
def handle_sso_callback():
    """Termine le flux SSO et redirige vers le client d'origine."""
    default_configuration = _get_sso_configuration()
    if not is_sso_enabled(default_configuration):
        return jsonify({"error": "SSO is not enabled"}), 404

    identity_provider_id = (
        session.pop("oidc_login_idp", None)
        or default_configuration["identity_provider_id"]
    )
    authentication_client = session.pop("oidc_login_client", "web_gui")
    next_path = session.pop("oidc_login_next", "")
    configuration = _get_identity_provider_configuration(identity_provider_id)

    if configuration is None:
        error_message = f"Unknown identity provider '{identity_provider_id}'"
        return _redirect_to_authentication_client(
            default_configuration,
            authentication_client,
            next_path,
            urlencode({"sso_error": error_message}),
        )

    # Première étape : traiter les erreurs renvoyées directement par Keycloak.
    identity_provider_error = request.args.get("error")
    if identity_provider_error:
        error_message = request.args.get(
            "error_description",
            identity_provider_error,
        )
        return _redirect_to_authentication_client(
            configuration,
            authentication_client,
            next_path,
            urlencode({"sso_error": error_message}),
        )

    # On vérifie le state avant d'échanger le code pour éviter qu'un autre flux
    # de connexion puisse réutiliser ce callback.
    authorization_code = request.args.get("code")
    received_state_token = request.args.get("state")
    expected_state_token = session.pop("oidc_state", None)
    state_is_invalid = (
        not authorization_code
        or not received_state_token
        or received_state_token != expected_state_token
    )
    if state_is_invalid:
        return _redirect_to_authentication_client(
            configuration,
            authentication_client,
            next_path,
            urlencode({"sso_error": "Invalid SSO state or missing code"}),
        )

    try:
        # Deuxième étape : Flask échange lui-même le code. Le secret du client
        # et les tokens Keycloak ne passent donc jamais dans le navigateur.
        keycloak_tokens = _exchange_authorization_code(
            configuration,
            authorization_code,
        )
        session["oidc_id_token"] = keycloak_tokens.get("id_token")
        session["oidc_idp"] = identity_provider_id

        # Troisième étape : on récupère l'identité fédérée et un token Keystone
        # non scopé, commun à la Web GUI et à JupyterHub.
        (
            unscoped_keystone_token,
            keystone_access_information,
        ) = _get_federated_keystone_identity(
            configuration,
            identity_provider_id,
            keycloak_tokens["access_token"],
        )

        # Un user fédéré doit avoir au moins un projet utilisable.
        available_projects = _list_keystone_projects(
            configuration["keystone_url"],
            unscoped_keystone_token,
        )
        if not available_projects:
            return _redirect_to_authentication_client(
                configuration,
                authentication_client,
                next_path,
                urlencode({"sso_error": "No project available for this user"}),
            )

        if authentication_client == "jupyterhub":
            # JupyterHub n'a pas besoin du token Keystone. On lui donne un ticket
            # court à usage unique, puis on détruit le token temporaire.
            user_id = keystone_access_information.user_id
            username = keystone_access_information.username
            if not user_id or not username:
                raise RuntimeError(
                    "Keystone did not return a federated user identity"
                )

            jupyterhub_ticket = JupyterTicketStore().issue(user_id, username)
            try:
                _revoke_keystone_token(
                    configuration,
                    unscoped_keystone_token,
                )
            except Exception:
                current_app.logger.warning(
                    "Could not revoke the temporary JupyterHub Keystone token"
                )

            return _redirect_to_authentication_client(
                configuration,
                authentication_client,
                next_path,
                urlencode({"flask_ticket": jupyterhub_ticket}),
            )

        # La Web GUI et le notebook ont besoin d'un token Keystone scopé sur
        # le projet choisi, exactement comme après une connexion locale.
        selected_project = _select_keystone_project(
            available_projects,
            configuration["preferred_project_name"],
        )
        scoped_authentication = Token(
            auth_url=configuration["keystone_url"],
            token=unscoped_keystone_token,
            project_id=selected_project["id"],
        )
        scoped_keystone_token = keystone_authentication_session.Session(
            auth=scoped_authentication
        ).get_token()

        if authentication_client == "notebook":
            NotebookAuthenticationStore().complete(
                next_path,
                scoped_keystone_token,
                selected_project["name"],
                selected_project["id"],
            )
            return _redirect_to_authentication_client(
                configuration,
                authentication_client,
                next_path,
                "",
            )

        return _redirect_to_web_gui(
            configuration,
            urlencode({
                "sso_token": scoped_keystone_token,
                "project": selected_project["name"],
                "project_id": selected_project["id"],
            }),
        )
    except Exception as exception:
        current_app.logger.exception("SSO callback failed")
        return _redirect_to_authentication_client(
            configuration,
            authentication_client,
            next_path,
            urlencode({"sso_error": str(exception)}),
        )
