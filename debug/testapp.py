from flask import Flask, request, jsonify, g
from keystoneauth1.identity import v3
from keystoneauth1 import session
from keystoneclient.v3 import client as keystone_client
import os

app = Flask(__name__)

# Si Flask est hors Docker -> localhost:5000, sinon -> keystone:5000
KEYSTONE_URL = os.getenv("KEYSTONE_URL", "http://localhost:5000/v3")


@app.route('/login', methods=['POST'])
def login():
    auth_data = request.json
    username = auth_data.get('username')
    password = auth_data.get('password')

    if not username or not password:
        return jsonify({"error": "Credentials missing"}), 400

    try:
        # 1. Création de l'identité (Authentification Password)
        auth = v3.Password(
            auth_url=KEYSTONE_URL,
            username=username,
            password=password,
            user_domain_name='Default',
            project_name='admin'  # On se scope sur un projet initial pour obtenir un token complet
        )

        # 2. Création de la session Keystone
        sess = session.Session(auth=auth)
        keystone = keystone_client.Client(session=sess)

        # 3. Récupération des infos utilisateur & Projets
        token_info = sess.get_auth_ref()  # Contient toutes les infos du token
        user_id = token_info.user_id

        # Récupération de la liste des projets auxquels l'utilisateur a accès
        projects = keystone.projects.list(user=user_id)

        project_list = []
        for p in projects:
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
    app.run(debug=True, port=3001)