import os
import json
from functools import wraps
from flask import request, g, jsonify
import flask

# Import du SDK OpenStack
import openstack
from openstack.exceptions import EndpointNotFound
from .datalake_authclient import AuthenticationClient


class OpenstackSDKAuthClient(AuthenticationClient):

    def __init__(self):
        self.current_app = flask.current_app
        self.KEYSTONE_URL = os.getenv("KEYSTONE_URL", "http://localhost:5000/v3")
        self.S3_ENDPOINT = os.getenv("S3_ENDPOINT", "http://10.5.10.1:8080")

    def _inject_token_in_response(self, response, token):
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

    def _enrich_user_info(self, user_dict, conn):
        """Enrichit user_dict avec projects et ec2_credentials en utilisant l'OpenStack SDK."""


        try:
            projects = list(conn.identity.user_projects(user_dict["id"]))
            user_dict["projects"] = [
                {
                    "id": p.id,
                    "name": p.name,
                    "description": getattr(p, 'description', None),
                    "enabled": p.is_enabled
                }
                for p in projects
            ]
        except Exception as e:
            self.current_app.logger.warning(f"Failed to fetch projects (check Keystone policy): {e}")
            user_dict["projects"] = []

        # 2. EC2 Credentials
        try:
            creds = list(conn.identity.credentials(user_id=user_dict["id"], type="ec2"))
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

            # CORRECTION : Aucun projet par défaut pour permettre l'authentification Unscoped
            project_name = request.headers.get("Project")

            # CASE 1: Bearer token
            if authorization and authorization.startswith("Bearer "):
                token = authorization.split(" ", 1)[1].strip()
                try:
                    auth_kwargs = {
                        "auth_url": self.KEYSTONE_URL,
                        "token": token,
                        "auth_type": "v3token"
                    }
                    if project_name:
                        auth_kwargs.update({
                            "project_name": project_name,
                            "project_domain_name": "Default"
                        })

                    conn = openstack.connect(**auth_kwargs)

                    access_info = conn.session.auth.get_access(conn.session)

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

                    if g.user["project_id"] and not g.user["preauthurl"]:
                        try:
                            g.user["preauthurl"] = conn.endpoint_for('object-store', interface='public')
                            if not g.user["preauthurl"]:
                                g.user["preauthurl"] = conn.endpoint_for('object-store', interface='internal')
                        except EndpointNotFound:
                            pass

                    self._enrich_user_info(g.user, conn)
                    return f(*args, **kwargs)

                except Exception as e:
                    self.current_app.logger.warning(f"Token validation failed: {e}")
                    return jsonify({"error": "Invalid or expired token"}), 401

            # CASE 2: Username + Password (LOCAL Keystone accounts only).
            #
            # Reserved for local Keystone users such as `admin` (break-glass
            # account, not in Keycloak). Federated users have no local password
            # and must authenticate via the SSO Authorization Code flow (the
            # "Keycloak" button). We deliberately do NOT use the OIDC password
            # grant (ROPC) here : it is deprecated (OAuth 2.0 Security BCP /
            # removed in OAuth 2.1) and would force the app to handle end-user
            # passwords. The classic login form is the secondary path for local
            # accounts only.
            if username and password:
                try:
                    auth_kwargs = {
                        "auth_url": self.KEYSTONE_URL,
                        "username": username,
                        "password": password,
                        "user_domain_name": 'Default',
                        "auth_type": "v3password"
                    }

                    if project_name:
                        auth_kwargs.update({
                            "project_name": project_name,
                            "project_domain_name": "Default"
                        })

                    conn = openstack.connect(**auth_kwargs)

                    access_token = conn.auth_token
                    access_info = conn.session.auth.get_access(conn.session)

                    preauthurl = None
                    # On ne cherche le endpoint object-store que si on est scopé sur un projet
                    if access_info.project_id:
                        try:
                            preauthurl = conn.endpoint_for('object-store', interface='public')
                            if not preauthurl:
                                preauthurl = conn.endpoint_for('object-store', interface='internal')
                        except EndpointNotFound:
                            preauthurl = None

                    g.user = {
                        "id": access_info.user_id,
                        "username": access_info.username,
                        "roles": access_info.role_names or [],
                        "project_id": access_info.project_id,
                        "project_name": access_info.project_name,
                        "source": "credentials",
                        "access_token": access_token,
                        "preauthurl": preauthurl,
                        "projects": [],
                        "ec2_credentials": None
                    }

                    self._enrich_user_info(g.user, conn)
                    response = f(*args, **kwargs)

                    return self._inject_token_in_response(response, access_token)

                except Exception as e:
                    self.current_app.logger.info(f"Login failure: {type(e).__name__} - {e}")
                    return jsonify({"error": "Invalid credentials"}), 401

            return jsonify({"error": "Authentication required",
                            "hint": "Use Bearer token or X-Username + X-Password headers"}), 401

        return decorated_function

    def _get_conn(self, project_name=None):
        """
        Crée une connexion fraîche avec le token actuel.
        Optionnel : forcer un project_name différent.
        """
        if not hasattr(g, 'user') or not g.user.get('access_token'):
            raise ValueError("Aucun token disponible dans g.user. Utilisez @login_required")

        auth_kwargs = {
            "auth_url": self.KEYSTONE_URL,
            "token": g.user["access_token"],
            "auth_type": "v3token",
        }

        # Si on veut forcer un projet différent (ex: admin project)
        if project_name:
            auth_kwargs.update({
                "project_name": project_name,
                "project_domain_name": "Default"
            })
        elif g.user.get("project_name"):
            auth_kwargs.update({
                "project_name": g.user["project_name"],
                "project_domain_name": "Default"
            })

        return openstack.connect(**auth_kwargs)

    # ------------------------------------------------------------------
    # 1. Liste des utilisateurs
    # ------------------------------------------------------------------
    def _list_users(self):
        """Liste tous les utilisateurs Keystone with all information : admin / test purpose"""
        conn = self._get_conn()
        users = list(conn.identity.users())
        return [u.to_dict() for u in users]


    def list_users(self):
        """Liste tous les utilisateurs Keystone (name + id)"""
        conn = self._get_conn()
        users = list(conn.identity.users())
        return [{"name":u.to_dict()["name"],"id":u.to_dict()["id"]} for u in users]

    def list_roles(self):
        conn = self._get_conn()

        self.current_app.logger.warning(conn)
        self.current_app.logger.warning(conn)

        return [(x.to_dict()["name"],x.to_dict()["id"])  for x in list(conn.identity.roles())]

    def list_roles_for_project(self, project_name: str):
        conn = self._get_conn(project_name=project_name)
        roles = list(conn.identity.roles())
        return [{"id": role.id, "name": role.name} for role in roles]

    def list_project_members(self, project_name: str):
        conn = self._get_conn(project_name=project_name)

        project = conn.identity.find_project(project_name, ignore_missing=True)
        if not project:
            return "Noproject"

        role_by_id = {role.id: role.name for role in conn.identity.roles()}
        user_by_id = {}
        try:
            user_by_id = {user.id: user.name for user in conn.identity.users()}
        except Exception as e:
            self.current_app.logger.warning(f"Unable to resolve usernames from role assignments: {e}")

        members = {}
        assignments = conn.identity.role_assignments(scope_project_id=project.id)
        for assignment in assignments:
            payload = assignment.to_dict() if hasattr(assignment, "to_dict") else {}

            scope = payload.get("scope", {}) if isinstance(payload, dict) else {}
            scoped_project = scope.get("project", {}) if isinstance(scope, dict) else {}
            scoped_project_id = scoped_project.get("id")
            if scoped_project_id and scoped_project_id != project.id:
                continue

            user_id = getattr(assignment, "user_id", None)
            if not user_id and isinstance(payload.get("user"), dict):
                user_id = payload["user"].get("id")
            if not user_id and isinstance(getattr(assignment, "user", None), dict):
                user_id = assignment.user.get("id")

            role_id = getattr(assignment, "role_id", None)
            if not role_id and isinstance(payload.get("role"), dict):
                role_id = payload["role"].get("id")
            if not role_id and isinstance(getattr(assignment, "role", None), dict):
                role_id = assignment.role.get("id")

            if not user_id:
                continue

            if user_id not in members:
                members[user_id] = {
                    "id": user_id,
                    "name": user_by_id.get(user_id, user_id),
                    "roles": []
                }

            role_name = role_by_id.get(role_id, role_id)
            if role_name and role_name not in members[user_id]["roles"]:
                members[user_id]["roles"].append(role_name)

        return list(members.values())

    def add_user_project(self,user,project_name):
        conn = self._get_conn()
        conn.identity.assign_project_role_to_user(conn.identity.find_project(project_name),user,conn.identity.get_role("member"))

    def remove_role_user_project(self,user,role,project_name):
        conn = self._get_conn()
        try:
            conn.identity.find_project(project_name).unassign_role_from_user(user,role)
        except Exception as e:
            self.current_app.logger.warning("ERROR" + e)

    def add_user_to_project(self, user_name: str, project_name: str, role_name: str = "member"):

        """Add a user to a project with a role (member by default)."""
        conn = self._get_conn(project_name=project_name)
        self.current_app.logger.warning("NOUVELLE VERSION")
        project = conn.identity.find_project(project_name, ignore_missing=True)
        if not project:
            return "Noproject"
        role = conn.identity.find_role(role_name, ignore_missing=True)
        if not role:
            return "Norole"
        user = conn.identity.find_user(user_name, ignore_missing=True, domain_id="default")
        if not user:
            user = conn.identity.find_user(user_name, ignore_missing=True)
        if not user:
            return "Nouser"
        memberrole = conn.identity.find_role("member")
        list_roles = list(conn.identity.roles())
        for role in list_roles:
            if conn.identity.validate_user_has_project_role(project,user, role):
                return {"status": "ok", "message": f" {user.name} user is already {role.name} in project {project.name}"}
        conn.identity.assign_project_role_to_user(project, user, memberrole)
        return {"status": "ok", "message": f"Role {memberrole.name} granted to {user.name} in {project.name}"}
    

    def set_user_roles_in_project(self, project_name: str, user_id: str, role_names):
        conn = self._get_conn(project_name=project_name)
        project = conn.identity.find_project(project_name, ignore_missing=True)
        if not project:
            return "Noproject"
        try:
            user = conn.identity.get_user(user_id)
        except Exception:
            user = None
        if user is None:
            return "Nouser"

        manageable_roles = {"reader", "member", "bucket_admin"}
        roles_by_name = {r.name: r for r in conn.identity.roles()}
        id_to_name = {r.id: name for name, r in roles_by_name.items()}

        unknown = [n for n in role_names if n not in roles_by_name]
        if unknown:
            return {"status": "Norole", "unknown_roles": unknown}

        def current_direct_roles():
            names = set()
            for a in conn.identity.role_assignments(scope_project_id=project.id):
                payload = a.to_dict() if hasattr(a, "to_dict") else {}
                uid = getattr(a, "user_id", None)
                if not uid and isinstance(payload.get("user"), dict):
                    uid = payload["user"].get("id")
                if uid != user.id:
                    continue
                rid = getattr(a, "role_id", None)
                if not rid and isinstance(payload.get("role"), dict):
                    rid = payload["role"].get("id")
                name = id_to_name.get(rid)
                if name:
                    names.add(name)
            return names & manageable_roles

        current = current_direct_roles()
        target = set(role_names) & manageable_roles

        to_remove = current - target
        to_add = target - current

        for name in to_remove:
            conn.identity.unassign_project_role_from_user(
                project=project.id, user=user.id, role=roles_by_name[name].id)
        for name in to_add:
            conn.identity.assign_project_role_to_user(
                project=project.id, user=user.id, role=roles_by_name[name].id)

        # Vérification sur les assignments DIRECTS (on ignore les rôles implicites).
        final = current_direct_roles()
        if final != target:
            return {
                "status": "error",
                "message": "Le changement de rôles n'a pas été entièrement appliqué",
                "expected": sorted(target),
                "actual": sorted(final),
            }
        return {
            "message": f"Roles updated for user {user.id} in project {project.name}",
            "roles": sorted(final),
        }








    def remove_user_from_project_by_name(self, project_name: str, user_id: str):
        conn = self._get_conn(project_name=project_name)

        self.current_app.logger.warning("project_name\n")
        self.current_app.logger.warning("project_name\n")
        self.current_app.logger.warning("project_name\n")
        self.current_app.logger.warning(project_name)
        project = conn.identity.find_project(project_name, ignore_missing=True)
        if not project:
            return "Noproject"
        user = None
        self.current_app.logger.warning("BITECOUILLE")
        try:
            user = conn.identity.get_user(user_id)

        except Exception:
            user = None
        if user is None:
            return "Nouser"
        # self.current_app.logger.warning(dir(conn.identity))
        self.current_app.logger.warning("BITECOUILLE")
        try:
            self.current_app.logger.warning("BITECOUILLE")
            list_roles = list(conn.identity.roles())
            self.current_app.logger.warning("C FAIT")
            self.current_app.logger.warning(list_roles)

        except Exception as e :
            self.current_app.logger(e)
        for role in list_roles:
            if conn.identity.validate_user_has_project_role(project, user, role):
                conn.identity.unassign_project_role_from_user(project, user, role)
        return {"message": f"User {user.id} removed from project {project.name}"}


    # ------------------------------------------------------------------
    # 2. Liste des rôles
    # ------------------------------------------------------------------
    # def list_roles(self):
    #     """Liste tous les rôles existants"""
    #     conn = self._get_conn()
    #     roles = list(conn.identity.roles())
    #     return [r.to_dict() for r in roles]

    # ------------------------------------------------------------------
    # 3. Ajouter un user à un projet
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # 4. Ajouter un rôle spécifique à un user dans un projet
    # ------------------------------------------------------------------
    def add_role_to_user_in_project(self, user_id: str, project_id: str, role_id: str):
        """Ajoute un rôle précis à un utilisateur sur un projet"""
        conn = self._get_conn()
        conn.identity.grant_role(role=role_id, user=user_id, project=project_id)
        return {"message": f"Rôle {role_id} ajouté à l'utilisateur {user_id} sur le projet {project_id}"}

    # ------------------------------------------------------------------
    # 5. Supprimer un user d'un projet (révoque tous ses rôles sur ce projet)
    # ------------------------------------------------------------------
    def remove_user_from_project(self, user_id: str, project_id: str):
        """Supprime complètement un utilisateur d'un projet"""
        conn = self._get_conn()
        assignments = list(conn.identity.role_assignments(
            user_id=user_id, project=project_id, effective=True
        ))

        for assignment in assignments:
            if assignment.role_id:
                conn.identity.revoke_role(
                    role=assignment.role_id,
                    user_id=user_id,
                    project=project_id
                )

        return {"message": f"Utilisateur {user_id} supprimé du projet {project_id}"}

    # ------------------------------------------------------------------
    # 6. Retirer un rôle spécifique d'un user dans un projet
    # ------------------------------------------------------------------
    def remove_role_from_user_in_project(self, user_id: str, project_id: str, role_id: str):
        """Retire un rôle précis d'un utilisateur sur un projet"""
        conn = self._get_conn()
        conn.identity.revoke_role(role=role_id, user=user_id, project=project_id)
        return {"message": f"Rôle {role_id} retiré de l'utilisateur {user_id} sur le projet {project_id}"}

