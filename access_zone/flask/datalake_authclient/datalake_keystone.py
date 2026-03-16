

from .datalake_authclient import AuthenticationClient
from functools import wraps
from flask import request, g, jsonify
import flask
import json
from keystoneauth1.identity import v3
from keystoneauth1 import session
from keystoneclient.v3 import client as keystone_client


class KeystoneClient(AuthenticationClient):

    def __init__(self):
        import os

        self.current_app = flask.current_app
        self.KEYSTONE_URL = os.getenv("KEYSTONE_URL", "http://localhost:5000/v3")
        self.S3_ENDPOINT = os.getenv("S3_ENDPOINT", "http://10.5.10.1:8080")

    def _make_session_from_auth(self, auth):
        """Crée une session Keystone à partir d'un objet auth."""
        return session.Session(auth=auth)

    def _inject_token_in_response(self,response, token):
        """
        Si la vue retourne (body, status) ou Response-like, injecte le token
        dans le body dict ou dans les headers (comportement existant conservé).
        """

        try:
            if isinstance(response, tuple) and len(response) >= 2 and response[1] in (200, 201):
                body = response[0]
                status = response[1]
                headers = dict(response[2]) if len(response) > 2 else {}
                if isinstance(body, dict):
                    body["access_token"] = token
                    body["projects"] = g.user.get("projects", [])
                    body["ec2_credentials"] = g.user.get("ec2_credentials")
                    return jsonify(body), status
                headers["X-Access-Token"] = token
                return response[0], status, headers
            elif hasattr(response, 'headers'):
                response.headers["X-Access-Token"] = token
                return response
        except Exception:
            self.current_app.logger.exception("Failed to inject token into response")
        return response

    def _enrich_user_info(self,user_dict, sess):
        """Enrichit user_dict avec projects et ec2_credentials (blob parsé si possible)."""
        keystone = keystone_client.Client(session=sess, include_metadata=True, endpoint_override=self.KEYSTONE_URL)

        # Projects
        try:
            projects = list(keystone.projects.list(user=user_dict["id"]).data)
            user_dict["projects"] = [
                {"id": p.id, "name": p.name, "description": getattr(p, 'description', None),
                 "enabled": getattr(p, 'enabled', True)}
                for p in projects
            ]
        except Exception as e:
            self.current_app.logger.warning(f"Failed to fetch projects: {e}")
            user_dict["projects"] = []

        # EC2 credentials (take first if present) and parse blob
        try:
            creds = list(keystone.credentials.list(user=user_dict["id"], type="ec2").data)
            if creds:
                ec2 = creds[0].to_dict()
                blob = ec2.get("blob")
                parsed = {}
                try:
                    if isinstance(blob, str):
                        parsed = json.loads(blob)
                    elif isinstance(blob, dict):
                        parsed = blob
                except Exception:
                    self.current_app.logger.warning("Failed to parse EC2 blob")
                ec2["blob"] = parsed
                user_dict["ec2_credentials"] = ec2
            else:
                user_dict["ec2_credentials"] = None
        except Exception as e:
            self.current_app.logger.warning(f"Failed to fetch EC2 credentials: {e}")
            user_dict["ec2_credentials"] = None

    def login_required(self, f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            print(request.headers)
            auth_header = request.headers.get("Authorization")
            username = request.headers.get("X-Username") or request.headers.get("Username")
            password = request.headers.get("X-Password") or request.headers.get("Password")
            print(request.headers)
            print(username)
            print(password)
            AUTH_URL = self.KEYSTONE_URL
            print("BIT1")
            print(AUTH_URL)
            # CASE 1: Bearer token
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ", 1)[1].strip()
                try:
                    auth = v3.Token(auth_url=AUTH_URL, token=token)
                    sess = self._make_session_from_auth(auth)
                    sess.get_token()  # validate
                    access_info = auth.auth_ref

                    g.user = {
                        "id": access_info.user_id,
                        "username": access_info.username,
                        "roles": access_info.role_names or [],
                        "project_id": access_info.project_id,
                        "project_name": access_info.project_name,
                        "source": "token",
                        "access_token": token,
                        "projects": [],
                        "ec2_credentials": None
                    }
                    self._enrich_user_info(g.user, sess)
                    return f(*args, **kwargs)
                except Exception as e:
                    self.current_app.logger.warning(f"Invalid token: {e}")
                    return jsonify({"error": "Invalid or expired token"}), 401

            # CASE 2: Username + Password
            if username and password:
                print("MIKONOS")
                try:
                    auth = v3.Password(
                        auth_url=AUTH_URL,
                        username=username,
                        password=password,
                        user_domain_name='Default',
                        project_domain_name='Default',
                        project_name='admin'
                    )
                    sess = self._make_session_from_auth(auth)
                    access_token = sess.get_token()
                    access_info = auth.auth_ref
                    print("CA MARCHE")
                    g.user = {
                        "id": access_info.user_id,
                        "username": access_info.username,
                        "roles": access_info.role_names or [],
                        "project_id": access_info.project_id,
                        "project_name": access_info.project_name,
                        "source": "credentials",
                        "access_token": access_token,
                        "projects": [],
                        "ec2_credentials": None
                    }

                    self._enrich_user_info(g.user, sess)
                    print("CA MARCHE")
                    response = f(*args, **kwargs)
                    print("CA MARCHE")
                    print(response)
                    # inject token + projects + ec2_credentials into response body or headers
                    return self._inject_token_in_response(response, access_token)
                except Exception as e:
                    self.current_app.logger.warning(f"Login failure: {type(e).__name__} - {e}")
                    return jsonify({"error": "Invalid credentials"}), 401

            print("BIT10 ")
            # No auth
            return jsonify({"error": "Authentication required",
                            "hint": "Use Bearer token or X-Username + X-Password headers"}), 401

        return decorated_function

