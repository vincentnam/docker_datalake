from flask import Flask, request, jsonify, g
from keystoneauth1.identity import v3
from keystoneauth1 import session
from keystoneclient.v3 import client as keystone_client
from keystoneclient.v3 import auth as auth_module
import os

app = Flask(__name__)

# Si Flask est hors Docker -> localhost:5000, sinon -> keystone:5000
KEYSTONE_URL = os.getenv("KEYSTONE_URL", "http://localhost:5000/v3")


@app.route('/login', methods=['POST'])
def login():
    print("TAMERE")
    # print(request.headers)
    auth_data = request.json
    username = auth_data.get('username')
    password = auth_data.get('password')
    print(username, password)
    # return "ouais"
    if not username or not password:
        return jsonify({"error": "Credentials missing"}), 400

    try:

        # 1. Création de l'identité (Authentification Password)
        auth = v3.Password(
            auth_url="http://localhost:5000/v3",
            username=username,
            password=password,
            user_domain_name='Default',
            project_domain_name='Default',
            project_name='admin'  # On se scope sur un projet initial pour obtenir un token complet
        )

        # 2. Création de la session Keystone
        sess = session.Session(auth=auth)
        keystone = keystone_client.Client(session=sess, include_metadata=True, endpoint_override="http://localhost:5000/v3")


        print("keystone")
        print(dir(keystone))
        print("sess")
        print(dir(sess))
        print("AUTH")
        print(dir(auth))
        print("project list")
        print(dir(keystone.projects))
        print(keystone.projects.list())
        print(dir(keystone.projects.list()))
        # print(keystone.projects.list().data)
        for i in keystone.projects.list().data:
            print(i)
        # 3. Récupération des infos utilisateur & Projets
        token = sess.get_token()  # déclenche l'auth si besoin → str

        # Récupère l'objet AccessInfoV3
        access_info = auth.auth_ref  # ← le bon endroit après get_token()
        keystone.projects.list(user=access_info.user_id)
        # ────────────────────────────────────────────────
        # 3. Extraction des infos (attributs corrects)
        # ────────────────────────────────────────────────
        user_id = access_info.user_id
        project_id = access_info.project_id
        project_name = access_info.project_name
        roles = access_info.role_names  # ← liste des noms de rôles
        expires = access_info.expires  # ← datetime.datetime

        # Optionnel : formatted strings
        expires_str = expires.isoformat() if expires else "N/A"
        roles_str = ", ".join(roles) if roles else "aucun rôle visible"

        print(f"Token (début)   : {token[:20]}...")
        print(f"User ID         : {user_id}")
        print(f"Project         : {project_name} ({project_id})")
        print(f"Roles           : {roles_str}")
        print(f"Expire le       : {expires_str}")

        # user_id = token.user_id
        # Récupération de la liste des projets auxquels l'utilisateur a accès
        # projects = keystone.projects.list(user=user_id)
        print("HE BAMBIN OH")
        # resp = keystone.projects.list()
        # print(resp)

        project_list = []
        for p in keystone.projects.list():
            project_list.append({
                "id": p.id,
                "name": p.name,
                "description": getattr(p, 'description', '')
            })

        # 4. Récupération des métadonnées (Roles sur le projet actuel)
        roles = [role['name'] for role in token_info.role_names]

        return jsonify({
            "status": "authenticated",
            "user": {
                "id": user_id,
                "username": username,
                "roles": roles,
                "projects": project_list
            },
            "token": sess.get_token(),  # Le token pour les futurs appels
            "catalog": token_info.service_catalog.catalog  # Liste des services (Swift, etc.)
        }), 200

    except Exception as e:
        app.logger.error(f"Erreur Keystone : {str(e)}")
        return jsonify({"error": "Login failed", "details": str(e)}), 401


if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=True, port=3001)