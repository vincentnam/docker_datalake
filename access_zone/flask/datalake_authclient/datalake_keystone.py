

from .datalake_authclient import AuthenticationClient
from functools import wraps
from flask import request, g, jsonify, current_app

import json
from keystoneauth1.identity import v3
from keystoneauth1 import session
from keystoneclient.v3 import client as keystone_client


class KeystoneClient(AuthenticationClient):

    def __init__(self, current_app):
        import os

        self.current_app = current_app
        self.KEYSTONE_URL = os.getenv("KEYSTONE_URL", "http://keystone:5000/v3")
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
            pass
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

            authorization = request.headers.get("Authorization")
            authurl = request.headers.get("X-Preauthurl") or request.headers.get("Preauthurl")

            username = request.headers.get("X-Username") or request.headers.get("Username")
            password = request.headers.get("X-Password") or request.headers.get("Password")
            try :
                project_name = request.headers.get("Project")
            except:
                project_name = "service"

            # CASE 1: Bearer token
            if authorization and authorization.startswith("Bearer "):
                token = authorization.split(" ", 1)[1].strip()
                try:
                    # Si on a un nom de projet, on demande à Keystone de "scoper" le token
                    auth_kwargs = {
                        "auth_url": self.KEYSTONE_URL,
                        "token": token
                    }
                    if project_name:
                        auth_kwargs.update({
                            "project_name": project_name,
                            "project_domain_name": "Default"
                        })

                    auth = v3.Token(**auth_kwargs)
                    sess = self._make_session_from_auth(auth)
                    access_info = auth.get_access(sess)  # Validation réelle ici

                    # On prépare l'objet utilisateur
                    g.user = {
                        "id": access_info.user_id,
                        "username": access_info.username,
                        "roles": access_info.role_names or [],
                        "project_id": access_info.project_id,
                        "project_name": access_info.project_name,
                        "source": "token",
                        "access_token": token,
                        "preauthurl": authurl
                    }

                    # Si on est scopé, on essaie de trouver l'URL Swift si elle n'est pas fournie
                    if g.user["project_id"] and not g.user["preauthurl"]:
                        try:
                            endpoints = access_info.service_catalog.get_endpoints(service_type='object-store')
                            for ep in endpoints.get('object-store', []):
                                if ep['interface'] in ('public', 'internal'):
                                    g.user["preauthurl"] = ep['url']
                                    break
                        except:
                            pass

                    # On enrichit les projets dispos (utile pour la GUI au login)
                    self._enrich_user_info(g.user, sess)
                    return f(*args, **kwargs)

                except Exception as e:
                    self.current_app.logger.warning(f"Token validation failed: {e}")
                    return jsonify({"error": "Invalid or expired token"}), 401


            # curl -X GET      -H "Authorization: Bearer gAAAAABpusSQsq7Rsxk3Ck-YM2jWr0pmsyEM8ummpdMjlD8smlsovQFVuYh5hjsRqSD33bjXCZlnQWG1S8ck1qvQKSSpRXOu9IuNCkyCbU-4LnkB86esLP39kgLoFD7HaU7sAmfc6ae9qzWQJUisdX9CLGmKqB78SsEjT5isq2bouU-EUKyFx-U"      -H "X-Preauthurl: http://management-1:8080/v1/AUTH_5ed1adce5246426bac2bf10ca69bcce2"      -H "Content-Type: application/json"      http://localhost:7000/api/buckets
            # CASE 2: Username + Password
            if username and password:

                try:
                    auth = v3.Password(
                        auth_url=self.KEYSTONE_URL,
                        username=username,
                        password=password,
                        user_domain_name='Default',
                        project_domain_name='Default',
                        project_name=project_name
                    )
                    sess = self._make_session_from_auth(auth)
                    access_token = sess.get_token()
                    access_info = auth.auth_ref


                    preauthurl = None
                    for ep in sess.auth.auth_ref.service_catalog.get_endpoints().get('object-store', []):
                        if ep['interface'] in ('public', 'internal'):
                            preauthurl = ep['url']
                            break

                    g.user = {
                        "id": access_info.user_id,
                        "username": access_info.username,
                        "roles": access_info.role_names or [],
                        "project_id": access_info.project_id,
                        "project_name": access_info.project_name,
                        "source": "credentials",
                        "access_token": access_token,
                        "preauthurl":preauthurl,
                        "projects": [],
                        "ec2_credentials": None
                    }

                    self._enrich_user_info(g.user, sess)

                    response = f(*args, **kwargs)

                    # inject token + projects + ec2_credentials into response body or headers
                    return self._inject_token_in_response(response, access_token)
                except Exception as e:
                    print(e)
                    self.current_app.logger.info(f"Login failure: {type(e).__name__} - {e}")
                    return jsonify({"error": "Invalid credentials"}), 401


            # No auth
            return jsonify({"error": "Authentication required",
                            "hint": "Use Bearer token or X-Username + X-Password headers"}), 401

        return decorated_function

