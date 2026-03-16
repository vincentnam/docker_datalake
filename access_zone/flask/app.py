# app.py - API REST Flask pour proxy S3 (Swift compat) - VERSION CLEAN

from flask import Flask, request, jsonify, send_file, abort, g, current_app
from flask_cors import CORS

from botocore.exceptions import ClientError
import io
from datetime import datetime
import os
from dotenv import load_dotenv


from datalake_authclient import get_auth
from datalake_objectstoreclient import get_storage


load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/buckets": {"origins": "*", "methods": ["GET", "POST", "OPTIONS"]},
                     r"/*": {"origins": "*", "methods": ["GET", "POST", "OPTIONS"]},
                     r"/buckets/*": {"origins": "*", "methods": ["GET", "POST", "DELETE", "OPTIONS"]}})
app.config['DEBUG'] = True

OBJECT_STORAGE_BACKEND = os.getenv("OBJECT_STORAGE_BACKEND", "swift").lower()  # "s3" ou "swift"
KEYSTONE_URL = os.getenv("KEYSTONE_URL", "http://localhost:5000/v3")
S3_ENDPOINT = os.getenv("S3_ENDPOINT", "http://10.5.10.1:8080")
AUTHENTICATION_BACKEND = os.getenv("AUTHENTICATION_BACKEND","keystone").lower()
authentication_client = get_auth(AUTHENTICATION_BACKEND)

# -----------------------
# Routes
# -----------------------
@app.route('/')
@authentication_client.login_required
def check_login():
    current_app.logger.debug("check_login g.user: %s", {k: v for k, v in g.user.items() if k != "access_token"})
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
        "access_token": g.user["access_token"]
    }), 200


@app.route('/buckets', methods=['GET'])
@authentication_client.login_required
def list_buckets():
    print("BITE")
    print(g)
    try:

        client = get_storage(OBJECT_STORAGE_BACKEND, authentication_client)
        print("CA MARCHE PAS")
        response = client.list_buckets()

        buckets = [
            {'Name': b['Name'], 'CreationDate': b['CreationDate'].isoformat() if 'CreationDate' in b else None}
            for b in response.get('Buckets', [])
        ]
        owner = {'DisplayName': response.get('Owner', {}).get('DisplayName'),
                 'ID': response.get('Owner', {}).get('ID')} if 'Owner' in response else None

        return jsonify({'buckets': buckets, 'owner': owner})
    except ClientError as e:
        current_app.logger.exception("Error listing buckets")
        abort(500, description=str(e))


@app.route('/buckets/<bucket>', methods=['DELETE'])
@authentication_client.login_required
def delete_bucket(bucket):
    try:
        current_app.logger.info('Deleting bucket %s', bucket)
        client = get_s3_client()
        client.delete_bucket(Bucket=bucket)
        return jsonify({'message': f'Bucket {bucket} deleted'}), 200
    except ClientError as e:
        current_app.logger.info(e)
        abort(404 if 'NoSuchBucket' in str(e) else 500, description=str(e))

print("bicuit")

@app.route('/buckets', methods=['POST'])
@authentication_client.login_required
def create_bucket():
    data = request.json or {}
    bucket_name = data.get('name')
    region = data.get('region', 'us-east-1')
    object_locking = bool(data.get('objectLocking', False))
    if not bucket_name:
        abort(400, description='Bucket name required')
    try:
        client = get_s3_client()
        config = {'LocationConstraint': region} if region else {}
        client.create_bucket()
        return jsonify({'message': f'Bucket {bucket_name} created'}), 201
    except ClientError as e:
        current_app.logger.info(e)
        abort(409 if 'BucketAlreadyExists' in str(e) or "BucketAlreadyOwnedByYou" in str(e) else 500,
              description=str(e) + ":" + str(getattr(e, 'response', None)))


@app.route('/buckets/<bucket>/objects', methods=['POST'])
@authentication_client.login_required
def upload_object(bucket):
    if 'file' not in request.files:
        abort(400, description='No file uploaded')
    file = request.files['file']
    key = request.form.get('key', file.filename)
    content_type = request.form.get('contentType', 'application/octet-stream')
    creation_date = request.form.get('creationDate', datetime.now().isoformat())
    try:
        client = get_s3_client()
        client.put_object(Bucket=bucket, Key=key, Body=file.stream.read(),
                          ContentType=content_type, Metadata={'CreationDate': creation_date})
        return jsonify({'message': f'Object {key} uploaded'}), 201
    except ClientError as e:
        current_app.logger.exception("Upload failed")
        abort(500, description=str(e))


@app.route('/buckets/<bucket>/objects', methods=['GET'])
@authentication_client.login_required
def list_objects(bucket):
    prefix = request.args.get('prefix', '')
    delimiter = request.args.get('delimiter', '/')
    try:
        client = get_s3_client()
        response = client.list_objects_v2(Bucket=bucket, Prefix=prefix, Delimiter=delimiter)

        objects = []
        for obj in response.get('Contents', []):
            key = obj['Key']
            try:
                head = client.head_object(Bucket=bucket, Key=key)
                obj_data = {
                    'key': key,
                    'size': obj['Size'],
                    'lastModified': obj['LastModified'].isoformat() if 'LastModified' in obj else None,
                    'eTag': obj.get('ETag', head.get('ETag')),
                    'storageClass': obj.get('StorageClass', head.get('StorageClass', 'STANDARD'))
                }
                metadata = {
                    'contentType': head.get('ContentType', 'application/octet-stream'),
                    'contentLength': head.get('ContentLength', obj['Size']),
                    'metadata': head.get('Metadata', {})
                }
                full_obj = {**obj_data, **{k: v for k, v in metadata.items() if v is not None}}
            except ClientError as head_err:
                current_app.logger.warning("HEAD failed for %s: %s", key, head_err)
                full_obj = {'key': key, 'size': obj['Size'],
                            'lastModified': obj['LastModified'].isoformat() if 'LastModified' in obj else None,
                            'eTag': obj.get('ETag'), 'storageClass': obj.get('StorageClass', 'STANDARD'),
                            'contentType': 'application/octet-stream'}
            objects.append(full_obj)

        prefixes = [{'prefix': p['Prefix']} for p in response.get('CommonPrefixes', [])]
        return jsonify({'objects': objects, 'prefixes': prefixes})
    except ClientError as e:
        current_app.logger.exception("List objects failed")
        abort(404 if 'NoSuchBucket' in str(e) else 500, description=str(e))


@app.route('/buckets/<bucket>/objects/<key>', methods=['GET'])
@authentication_client.login_required
def download_object(bucket, key):
    try:
        client = get_s3_client()
        response = client.get_object(Bucket=bucket, Key=key)
        return send_file(io.BytesIO(response['Body'].read()), as_attachment=True, download_name=key)
    except ClientError as e:
        current_app.logger.exception("Download failed")
        abort(404 if 'NoSuchKey' in str(e) else 500, description=str(e))


@app.route('/buckets/<bucket>/objects/<key>', methods=['DELETE'])
@authentication_client.login_required
def delete_object(bucket, key):
    try:
        client = get_s3_client()
        client.delete_object(Bucket=bucket, Key=key)
        return jsonify({'message': f'Object {key} deleted'})
    except ClientError as e:
        current_app.logger.exception("Delete object failed")
        abort(404 if 'NoSuchKey' in str(e) else 500, description=str(e))


@app.route('/debug/list-buckets-test', methods=['GET'])
def debug_list_buckets():
    """
    Test rapide : s'authentifie en Password (admin/admin), enrichit g.user,
    crée un client S3 et retourne la liste des buckets.
    """
    try:
        # 1) Authentification Keystone avec admin/admin
        auth = v3.Password(
            auth_url=KEYSTONE_URL,
            username='admin',
            password='admin',
            user_domain_name='Default',
            project_domain_name='Default',
            project_name='admin'
        )
        sess = session.Session(auth=auth)
        token = sess.get_token()
        access_info = auth.auth_ref

        # 2) Remplir g.user comme le décorateur le ferait
        g.user = {
            "id": access_info.user_id,
            "username": access_info.username,
            "roles": access_info.role_names or [],
            "project_id": access_info.project_id,
            "project_name": access_info.project_name,
            "source": "credentials",
            "access_token": token,
            "projects": [],
            "ec2_credentials": None
        }

        # 3) Enrichir (projects + ec2) avec ta fonction existante
        enrich_user_info(g.user, sess)

        # 4) Créer client S3 et lister les buckets (réutilise get_s3_client)
        client = get_s3_client()
        resp = client.list_buckets()

        buckets = [
            {"Name": b.get("Name"), "CreationDate": b.get("CreationDate").isoformat() if b.get("CreationDate") else None}
            for b in resp.get("Buckets", [])
        ]
        owner = {"DisplayName": resp.get("Owner", {}).get("DisplayName"), "ID": resp.get("Owner", {}).get("ID")} if resp.get("Owner") else None

        return jsonify({"status": "ok", "buckets": buckets, "owner": owner, "ec2_credentials_present": bool(g.user.get("ec2_credentials"))}), 200

    except Exception as e:
        current_app.logger.exception("Debug list-buckets failed")
        return jsonify({"status": "error", "error": str(e)}), 500


# from swiftclient.client import Connection
#
# conn = Connection(
#     authurl='http://localhost:5000/v3',
#     user='swift',
#     key='testing',
#     os_options={'project_name': 'service', 'user_domain_name': 'Default', 'project_domain_name': 'Default'},
#     auth_version='3'
# )
#
# # lister containers
# containers = conn.get_account()[1]
# print([c['name'] for c in containers])
#

# ########################################
#
# # CA MARCHE :
# from swiftclient import client as swiftclient
# conn = swiftclient.Connection("http://keystone:5000/v3",
#                                          "admin",
#                                          "admin",
#                               os_options={'project_name': 'admin', 'user_domain_name': 'Default', 'project_domain_name': 'Default'},
#                                          auth_version="3")
# #########################################
#



@app.route("/flask-health-check", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=3001)
