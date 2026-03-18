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

#TODO : Handle error when error are raised in clients
load_dotenv()

app = Flask(__name__)

CORS(app, resources={r"/buckets": {"origins": "*", "methods": ["GET", "POST", "OPTIONS"]},
                     r"/*": {"origins": "*", "methods": ["GET", "POST", "OPTIONS"]},
                     r"/buckets/*": {"origins": "*", "methods": ["GET", "POST", "DELETE", "OPTIONS"]}})
app.config['DEBUG'] = True

OBJECT_STORAGE_BACKEND = os.getenv("OBJECT_STORAGE_BACKEND", "swift").lower()  # "s3" ou "swift"
KEYSTONE_URL = os.getenv("KEYSTONE_URL", "http://keystone:5000/v3")
S3_ENDPOINT = os.getenv("S3_ENDPOINT", "http://10.5.10.1:8080")
AUTHENTICATION_BACKEND = os.getenv("AUTHENTICATION_BACKEND","keystone").lower()
authentication_client = get_auth(AUTHENTICATION_BACKEND,current_app=app)




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



if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=5000)
