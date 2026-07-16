"""JupyterHub authenticator delegating local login to Flask."""

import json

from jupyterhub.auth import Authenticator
from tornado.httpclient import AsyncHTTPClient, HTTPClientError, HTTPRequest
from traitlets import Float, Unicode


class FlaskLocalAuthenticator(Authenticator):
    """Authenticate local or federated Keystone identities through Flask."""

    flask_base_url = Unicode(
        "http://flask-app:5000",
        config=True,
        help="Internal URL of the Flask API.",
    )
    request_timeout = Float(
        10.0,
        config=True,
        help="Timeout, in seconds, for the Flask authentication request.",
    )

    async def authenticate(self, handler, data):
        ticket = data.get("flask_ticket") or ""
        if ticket:
            endpoint = "/auth/jupyter/ticket"
            request_body = {"ticket": ticket}
            login_label = "federated SSO ticket"
            username = None
        else:
            username = (data.get("username") or "").strip()
            password = data.get("password") or ""
            if not username or not password:
                return None
            endpoint = "/auth/jupyter/local"
            request_body = {"username": username, "password": password}
            login_label = f"local Keystone login for user {username}"

        request = HTTPRequest(
            url=f"{self.flask_base_url.rstrip('/')}{endpoint}",
            method="POST",
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            body=json.dumps(request_body),
            connect_timeout=self.request_timeout,
            request_timeout=self.request_timeout,
        )

        try:
            response = await AsyncHTTPClient().fetch(request)
        except HTTPClientError as exc:
            if exc.code == 401:
                self.log.warning("Flask rejected %s", login_label)
            else:
                self.log.error(
                    "Flask authentication request failed for %s: HTTP %s",
                    login_label,
                    exc.code,
                )
            return None
        except Exception as exc:
            self.log.error(
                "Flask authentication service unavailable for %s: %s",
                login_label,
                type(exc).__name__,
            )
            return None

        try:
            payload = json.loads(response.body.decode("utf-8"))
            user = payload["user"]
            authenticated_username = user["username"]
            user_id = user["id"]
        except (KeyError, TypeError, ValueError, UnicodeDecodeError):
            self.log.error("Flask returned an invalid authentication response")
            return None

        if not payload.get("authenticated") or not authenticated_username or not user_id:
            return None

        return {"name": authenticated_username}
