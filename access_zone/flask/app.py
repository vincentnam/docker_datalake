# app.py - API REST Flask pour proxy S3 (Swift compat) - VERSION CLEAN

from flask import Flask, request, jsonify, send_file, abort, g, current_app, make_response
from flask_cors import CORS

from botocore.exceptions import ClientError
import io
from datetime import datetime
import os
from dotenv import load_dotenv


from datalake_authclient import get_auth
from datalake_objectstoreclient import get_storage
from datalake_jupyter_auth import jupyter_auth_bp
from datalake_sso import sso_bp






import traceback



#TODO : Handle error when error are raised in clients
load_dotenv()

app = Flask(__name__)
app.config["DEBUG"] = False

CORS(app, resources={r"/buckets": {"origins": "*", "methods": ["GET", "POST", "OPTIONS"]},
                     r"/*": {"origins": "*", "methods": ["GET", "POST", "OPTIONS"]},
                     r"/buckets/*": {"origins": "*", "methods": ["GET", "POST", "DELETE", "OPTIONS"]}})
app.config['DEBUG'] = True
# Secret key used to sign the OIDC SSO state cookie (see datalake_sso.py)
app.secret_key = os.getenv("FLASK_SECRET", "dev-insecure-change-me")
# Keycloak SSO endpoints : /auth/login, /auth/callback, /auth/config
app.register_blueprint(sso_bp)
# JupyterHub local login connector : /auth/jupyter/local
app.register_blueprint(jupyter_auth_bp)

OBJECT_STORAGE_BACKEND = os.getenv("OBJECT_STORAGE_BACKEND", "swift").lower()  # "s3" ou "swift"
KEYSTONE_URL = os.getenv("KEYSTONE_URL", "http://keystone:5000/v3")
S3_ENDPOINT = os.getenv("S3_ENDPOINT", "http://10.5.10.1:8080")
AUTHENTICATION_BACKEND = os.getenv("AUTHENTICATION_BACKEND","openstack").lower()
authentication_client = get_auth(AUTHENTICATION_BACKEND)

print(authentication_client)

PROJECT_MANAGEABLE_ROLES = {"reader", "member", "bucket_admin", "bucket_owner"}


def _extract_http_status_code(exc, default=500):
    status = getattr(exc, "status_code", None) or getattr(exc, "http_status", None)
    if not status and getattr(exc, "response", None) is not None:
        status = getattr(exc.response, "status_code", None)
    if not status:
        message = str(exc).lower()
        if "forbidden" in message:
            status = 403
        elif "unauthorized" in message:
            status = 401
        elif "not found" in message:
            status = 404
        elif "conflict" in message:
            status = 409
        else:
            status = default
    return int(status)


def _error_response(exc, default=500):
    status = _extract_http_status_code(exc, default=default)
    return jsonify({"error": str(exc)}), status


# -----------------------
# Routes
# -----------------------
@app.route('/')
@authentication_client.login_required
def check_login():

    # current_app.logger.debug("check_login g.user: %s", {k: v for k, v in g.user.items() if k != "access_token"})
    return jsonify({
        "status": "authenticated",
        "user": {
            "id": g.user["id"],
            "username": g.user["username"],
            "email": g.user.get("email"),
            "source": g.user.get("source", "unknown"),
            "roles": g.user.get("roles", []),
            "project_id": g.user.get("project_id"),
            "project_name": g.user.get("project_name"),
            "projects": g.user.get("projects", []),
            "ec2_credentials": g.user.get("ec2_credentials")
        },
        "access_token": g.user["access_token"],
        "preauthurl": g.user.get("preauthurl")
    }), 200




@app.route('/buckets', methods=['GET'])
@authentication_client.login_required
def list_buckets():
    '''
    Curl parameter for this route :
    ======= Authentication specific header parameter
    X-Username OR Username : account username
    X-Password OR Password : Account password to authenticate

    OR "Authorization: Bearer " + access_token

    Project : Project / environnement name (not ID) ; default value : service
    ======= Route specific header parameter


    '''

    #TODO: Project with project id instead of project name (with swift backend) result in authentication error - fix needed
    try:
        # password =         request.headers.get("Password") or         request.headers.get("X-Password")
        client = get_storage(OBJECT_STORAGE_BACKEND, authentication_client,token=g.user["access_token"], preauthurl=g.user["preauthurl"],  current_app = current_app)
        # client = get_storage(OBJECT_STORAGE_BACKEND, authentication_client,user=g.user["username"], password=password, project_name = g.user["project_name"],  current_app = current_app)
        data = client.list_buckets()
        return {
            "buckets": data['Buckets'],
            "owner": data['Owner']
        }
        return jsonify({'buckets': buckets, 'owner': owner})
    except ClientError as e:
        current_app.logger.exception("Error listing buckets")
        abort(500, description=str(e))


# @app.route('/buckets/<bucket>', methods=['DELETE'])
# @authentication_client.login_required
# def delete_bucket(bucket):
#     try:
#         current_app.logger.info('Deleting bucket %s', bucket)
#         client = get_s3_client()
#         client.delete_bucket(Bucket=bucket)
#         return jsonify({'message': f'Bucket {bucket} deleted'}), 200
#     except ClientError as e:
#         current_app.logger.info(e)
#         abort(404 if 'NoSuchBucket' in str(e) else 500, description=str(e))
#

@app.route('/buckets/<bucket>', methods=['DELETE'])
@authentication_client.login_required
def delete_bucket(bucket):
    '''
    Curl parameter for this route :
    ======= Authentication specific header parameter
    X-Username OR Username : account username
    X-Password OR Password : Account password to authenticate

    OR "Authorization: Bearer " + access_token

    Project : Project / environnement name (not ID) ; default value : service
    ======= Route specific header parameter


    '''
    try:
        # current_app.logger.info('Deleting bucket %s', bucket)
        client = get_storage(
            OBJECT_STORAGE_BACKEND,
            authentication_client,
            token=g.user["access_token"],
            preauthurl=g.user["preauthurl"],
            current_app=current_app
        )

        client.delete_bucket(name=bucket)

        return jsonify({'message': f'Bucket "{bucket}" deleted'}), 200

    except Exception as e:

        current_app.logger.exception(f"Error deleting bucket {bucket}")

        error_msg = str(e)
        if 'NoSuchBucket' in error_msg or 'Not Found' in error_msg:
            abort(404, description=error_msg)
        else:
            abort(500, description=error_msg)


@app.route('/buckets/<bucket>', methods=['HEAD'])
@authentication_client.login_required
def head_bucket(bucket):
    try:
        client = get_storage(OBJECT_STORAGE_BACKEND, authentication_client,
                             token=g.user["access_token"], preauthurl=g.user["preauthurl"], current_app=current_app)

        headers = client.head_bucket(name=bucket)

        # Flask gère automatiquement le fait de ne pas envoyer de body pour HEAD
        # Mais on s'assure que les headers sont bien des chaînes de caractères
        response_headers = {str(k): str(v) for k, v in headers.items()}

        return make_response("", 200, response_headers)
    except Exception as e:
        current_app.logger.error(f"HEAD Bucket failed: {e}")
        abort(404 if 'Not Found' in str(e) else 500)


@app.route('/buckets/<bucket>', methods=['POST'])
@authentication_client.login_required
def create_bucket(bucket):

    try:
        client = get_storage(
            OBJECT_STORAGE_BACKEND,
            authentication_client,
            token=g.user["access_token"],
            preauthurl=g.user["preauthurl"],
            current_app=current_app
        )

        client.create_bucket(name=bucket)
        return jsonify({'message': f'Bucket {bucket} created'}), 201

    except Exception as e:
        current_app.logger.exception("Error creating bucket")
        error_msg = str(e)
        abort(409 if 'Conflict' in error_msg or 'exists' in error_msg.lower() else 500, description=error_msg)


@app.route('/buckets/<bucket>/objects', methods=['POST'])
@authentication_client.login_required
def upload_object(bucket):
    if 'file' not in request.files:
        abort(400, description='No file uploaded')

    file = request.files['file']
    key = request.form.get('key', file.filename)
    content_type = request.form.get('contentType', 'application/octet-stream')

    try:
        client = get_storage(
            OBJECT_STORAGE_BACKEND,
            authentication_client,
            token=g.user["access_token"],
            preauthurl=g.user["preauthurl"],
            current_app=current_app
        )

        client.upload_object(
            bucket=bucket,
            key=key,
            file_obj=file.stream.read(),  # On lit les bytes du fichier
            content_type=content_type
        )

        return jsonify({'message': f'Object {key} uploaded'}), 201

    except Exception as e:
        current_app.logger.exception("Upload failed")
        abort(500, description=str(e))


@app.route('/buckets/<bucket>/objects', methods=['GET'])
@authentication_client.login_required
def list_objects(bucket):
    prefix = request.args.get('prefix', '')
    delimiter = request.args.get('delimiter', '/')

    try:
        client = get_storage(
            OBJECT_STORAGE_BACKEND,
            authentication_client,
            token=g.user["access_token"],
            preauthurl=g.user["preauthurl"],
            current_app=current_app
        )

        # Le client renvoie directement le bon format JSON
        data = client.list_objects(bucket=bucket, prefix=prefix, delimiter=delimiter)
        return jsonify(data)

    except Exception as e:
        current_app.logger.exception("List objects failed")
        abort(404 if 'Not Found' in str(e) else 500, description=str(e))


@app.route('/buckets/<bucket>/objects/<key>', methods=['GET'])
@authentication_client.login_required
def download_object(bucket, key):
    try:
        client = get_storage(
            OBJECT_STORAGE_BACKEND,
            authentication_client,
            token=g.user["access_token"],
            preauthurl=g.user["preauthurl"],
            current_app=current_app
        )

        # Le client nous renvoie les bytes directs
        file_bytes = client.download_object(bucket=bucket, key=key)

        return send_file(
            io.BytesIO(file_bytes),
            as_attachment=True,
            download_name=key
        )

    except Exception as e:
        current_app.logger.exception("Download failed")
        abort(404 if 'Not Found' in str(e) else 500, description=str(e))


@app.route('/buckets/<bucket>/objects/<key>', methods=['DELETE'])
@authentication_client.login_required
def delete_object(bucket, key):
    try:
        client = get_storage(
            OBJECT_STORAGE_BACKEND,
            authentication_client,
            token=g.user["access_token"],
            preauthurl=g.user["preauthurl"],
            current_app=current_app
        )

        client.delete_object(bucket=bucket, key=key)
        return jsonify({'message': f'Object {key} deleted'}), 200

    except Exception as e:
        current_app.logger.exception("Delete object failed")
        abort(404 if 'Not Found' in str(e) else 500, description=str(e))


@app.route('/buckets/<bucket>/objects/<key>', methods=['HEAD'])
@authentication_client.login_required
def head_object(bucket, key):
    try:
        client = get_storage(OBJECT_STORAGE_BACKEND, authentication_client,
                             token=g.user["access_token"], preauthurl=g.user["preauthurl"], current_app=current_app)

        headers = client.head_object(bucket=bucket, key=key)
        current_app.logger.warning(headers)
        # On renvoie tous les headers bruts (incluant tes métadonnées personnalisées)
        return '', 200, headers
    except Exception as e:

        abort(404 if 'Not Found' in str(e) else 500)


@app.route("/flask-health-check", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

@app.route('/users', methods=['GET'])
@authentication_client.login_required
def get_users_list():
    try:
        client = authentication_client
        return jsonify(client.list_users()), 200
    except Exception as e:
        return _error_response(e)

@app.route('/roles', methods=['GET'])
@authentication_client.login_required
def get_roles():
    """
    Return the role of user in the current project (in authenticated project).

    Returns:
        list[(string,string)] : [(name,id),...] : list of information about role of the user in the project
    """
    try:
        client = authentication_client
        return jsonify(client.list_roles()), 200
    except Exception as e:
        return _error_response(e)

@app.route('/projects/<project_name>/users', methods=['POST'])
@authentication_client.login_required
def add_user_to_project(project_name):
    try:
        if not hasattr(authentication_client, "add_user_to_project"):
            return jsonify({"error": "Operation not supported by authentication backend"}), 501
        payload = request.get_json(silent=True) or {}
        current_app.logger.warning(payload)
        # TODO: Change to header to unify
        user = payload.get("username")
        role = payload.get("role", "member")
        # current_app.logger.warning(role)
        #
        # role = role.strip() if isinstance(role, str) else role
        # current_app.logger.warning(role)
        if not user:
            return jsonify({"error": "Missing username"}), 400
        if role not in PROJECT_MANAGEABLE_ROLES:
            return jsonify({"error": f"Unsupported role '{role}'"}), 400

        authclient = authentication_client
        current_app.logger.warning("COUILLE")

        adduser_resp = authclient.add_user_to_project(user, project_name, role)
        current_app.logger.warning("adduser_resp")
        current_app.logger.warning(adduser_resp)


        if adduser_resp is True or (isinstance(adduser_resp, dict) and adduser_resp.get("status") == "ok"):
            return jsonify({"message": f"User added to project {project_name}"}), 201
        elif adduser_resp == "Nouser":
            return jsonify({"error": f"User {user} doesn't exist."}), 404
        elif adduser_resp == "Noproject":
            return jsonify({"error": f"Project {project_name} doesn't exist."}), 404
        elif adduser_resp == "Norole":
            return jsonify({"error": f"Role {role} doesn't exist."}), 404
        elif adduser_resp in ("UserAlreadyIn", "UserAlreadyInRole"):
            return jsonify({"message": f"User {user} already has role {role} in project {project_name}."}), 200
        return jsonify({"error": "User not added to project."}), 403
    except Exception as e:
        return _error_response(e)


@app.route('/projects/<project_name>/members', methods=['GET'])
@authentication_client.login_required
def get_project_members(project_name):
    try:
        if not hasattr(authentication_client, "list_project_members"):
            return jsonify({"error": "Operation not supported by authentication backend"}), 501
        client = authentication_client
        members = client.list_project_members(project_name)
        current_app.logger.warning(members)
        if members == "Noproject":
            return jsonify({"error": f"Project {project_name} doesn't exist."}), 404
        return jsonify({"project": project_name, "members": members}), 200
    except Exception as e:
        return _error_response(e)


@app.route('/projects/<project_name>/roles', methods=['GET'])
@authentication_client.login_required
def get_project_roles(project_name):
    try:
        if not hasattr(authentication_client, "list_roles_for_project"):
            return jsonify({"error": "Operation not supported by authentication backend"}), 501
        client = authentication_client
        roles = client.list_roles_for_project(project_name)
        return jsonify({"project": project_name, "roles": roles}), 200
    except Exception as e:
        return _error_response(e)

@app.route('/projects/<project_name>/users/<user_id>/roles', methods=['PUT'])
@authentication_client.login_required
def update_user_roles(project_name, user_id):

    try:
        if not hasattr(authentication_client, "set_user_roles_in_project"):
            return jsonify({"error": "Operation not supported by authentication backend"}), 501
        payload = request.get_json(silent=True) or {}
        roles = payload.get("roles", [])
        if not isinstance(roles, list):
            return jsonify({"error": "roles must be a list"}), 400
        if not all(isinstance(role_name, str) for role_name in roles):
            return jsonify({"error": "roles must contain only strings"}), 400
        unsupported_roles = sorted(set(role_name for role_name in roles if role_name not in PROJECT_MANAGEABLE_ROLES))
        if unsupported_roles:
            return jsonify({"error": "Unsupported roles", "unsupported_roles": unsupported_roles}), 400
        current_app.logger.warning("ROLES SALUT : ")
        current_app.logger.warning(roles)
        client = authentication_client
        resp = client.set_user_roles_in_project(project_name, user_id, roles)
        
        if resp == "Noproject":
            return jsonify({"error": f"Project {project_name} doesn't exist."}), 404
        if resp == "Nouser":
            return jsonify({"error": f"User {user_id} doesn't exist."}), 404
        if isinstance(resp, dict) and resp.get("status") == "Norole":
            return jsonify({"error": "Unknown roles", "unknown_roles": resp.get("unknown_roles", [])}), 400

        return jsonify(resp), 200
    except Exception as e:
        current_app.logger.warning(traceback.format_exc())
        current_app.logger.warning(e)
        return jsonify({"error": str(e)}), 500


@app.route('/projects/<project_name>/users/<user_id>', methods=['DELETE'])
@authentication_client.login_required
def remove_user_from_project(project_name, user_id):
    try:
        if not hasattr(authentication_client, "remove_user_from_project_by_name"):
            return jsonify({"error": "Operation not supported by authentication backend"}), 501
        client = authentication_client
        resp = client.remove_user_from_project_by_name(project_name, user_id)
        current_app.logger.warning(resp)
        if resp == "Noproject":
            return jsonify({"error": f"Project {project_name} doesn't exist."}), 404
        if resp == "Nouser":
            return jsonify({"error": f"User {user_id} doesn't exist."}), 404
        return jsonify(resp), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)

