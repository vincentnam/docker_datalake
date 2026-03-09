# app.py - API REST Flask pour proxy S3 (Swift compat) - VERSION CLEAN
from functools import wraps
from flask import Flask, request, jsonify, send_file, abort, g, current_app
from flask_cors import CORS
import boto3
from botocore.exceptions import ClientError
import io
from datetime import datetime
import os
from dotenv import load_dotenv
import json

from keystoneauth1.identity import v3
from keystoneauth1 import session
from keystoneclient.v3 import client as keystone_client

load_dotenv()
KEYSTONE_URL = os.getenv("KEYSTONE_URL", "http://localhost:5000/v3")
S3_ENDPOINT = os.getenv("S3_ENDPOINT", "http://10.5.10.1:8080")

app = Flask(__name__)
CORS(app, resources={r"/buckets": {"origins": "*", "methods": ["GET", "POST", "OPTIONS"]},
                     r"/*": {"origins": "*", "methods": ["GET", "POST", "OPTIONS"]},
                     r"/buckets/*": {"origins": "*", "methods": ["GET", "POST", "DELETE", "OPTIONS"]}})
app.config['DEBUG'] = True


# -----------------------
# Helpers
# -----------------------
def _make_session_from_auth(auth):
    """Crée une session Keystone à partir d'un objet auth."""
    return session.Session(auth=auth)


def _inject_token_in_response(response, token):
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
        current_app.logger.exception("Failed to inject token into response")
    return response


# -----------------------
# Enrich user info
# -----------------------
def enrich_user_info(user_dict, sess):
    """Enrichit user_dict avec projects et ec2_credentials (blob parsé si possible)."""
    keystone = keystone_client.Client(session=sess, include_metadata=True, endpoint_override=KEYSTONE_URL)

    # Projects
    try:
        projects = list(keystone.projects.list(user=user_dict["id"]).data)
        user_dict["projects"] = [
            {"id": p.id, "name": p.name, "description": getattr(p, 'description', None), "enabled": getattr(p, 'enabled', True)}
            for p in projects
        ]
    except Exception as e:
        current_app.logger.warning(f"Failed to fetch projects: {e}")
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
                current_app.logger.warning("Failed to parse EC2 blob")
            ec2["blob"] = parsed
            user_dict["ec2_credentials"] = ec2
        else:
            user_dict["ec2_credentials"] = None
    except Exception as e:
        current_app.logger.warning(f"Failed to fetch EC2 credentials: {e}")
        user_dict["ec2_credentials"] = None


# -----------------------
# Auth decorator
# -----------------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_app.logger.info("COUCOU")
        auth_header = request.headers.get("Authorization")
        username = request.headers.get("X-Username") or request.headers.get("Username")
        password = request.headers.get("X-Password") or request.headers.get("Password")

        AUTH_URL = KEYSTONE_URL

        # CASE 1: Bearer token
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1].strip()
            try:
                auth = v3.Token(auth_url=AUTH_URL, token=token)
                sess = _make_session_from_auth(auth)
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
                enrich_user_info(g.user, sess)
                return f(*args, **kwargs)
            except Exception as e:
                current_app.logger.warning(f"Invalid token: {e}")
                return jsonify({"error": "Invalid or expired token"}), 401

        # CASE 2: Username + Password
        if username and password:
            try:
                auth = v3.Password(
                    auth_url=AUTH_URL,
                    username=username,
                    password=password,
                    user_domain_name='Default',
                    project_domain_name='Default',
                    project_name='admin'
                )
                sess = _make_session_from_auth(auth)
                access_token = sess.get_token()
                access_info = auth.auth_ref

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

                enrich_user_info(g.user, sess)

                response = f(*args, **kwargs)
                # inject token + projects + ec2_credentials into response body or headers
                return _inject_token_in_response(response, access_token)
            except Exception as e:
                current_app.logger.warning(f"Login failure: {type(e).__name__} - {e}")
                return jsonify({"error": "Invalid credentials"}), 401

        # No auth
        return jsonify({"error": "Authentication required", "hint": "Use Bearer token or X-Username + X-Password headers"}), 401

    return decorated_function


# -----------------------
# S3 client factory
# -----------------------
def get_s3_client():
    """
    Retourne un client boto3.
    Priorité :
      1) EC2 credentials (access + secret) si disponibles dans g.user["ec2_credentials"]
      2) Fallback : token Keystone (aws_access_key_id=token, aws_session_token=token)
    """
    if not hasattr(g, 'user') or 'access_token' not in g.user:
        abort(401, description="Authentication required")

    token = g.user['access_token']

    # Try EC2 credentials first
    ec2 = g.user.get('ec2_credentials')
    if ec2 and isinstance(ec2, dict):
        blob = ec2.get('blob') or {}
        access_key = None
        secret_key = None
        try:
            if isinstance(blob, dict):
                access_key = blob.get('access') or blob.get('access_key') or blob.get('accessKey')
                secret_key = blob.get('secret') or blob.get('secret_key') or blob.get('secretKey')
            elif isinstance(blob, str):
                parsed = json.loads(blob)
                access_key = parsed.get('access')
                secret_key = parsed.get('secret')
        except Exception as e:
            current_app.logger.warning(f"Failed to parse EC2 blob in get_s3_client: {e}")

        if access_key and secret_key:
            current_app.logger.info("Using EC2 credentials for S3 client (access/secret).")
            return boto3.client(
                's3',
                endpoint_url=S3_ENDPOINT,
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name='us-east-1',
                config=boto3.session.Config(signature_version='s3v4', s3={'addressing_style': 'path'})
            )

    # Fallback: use Keystone token (some middlewares accept aws_session_token)
    current_app.logger.info("No EC2 credentials found, falling back to Keystone token for S3 client.")
    return boto3.client(
        's3',
        endpoint_url=S3_ENDPOINT,
        aws_access_key_id=token,
        aws_secret_access_key='',
        aws_session_token=token,
        region_name='us-east-1',
        config=boto3.session.Config(signature_version='s3v4', s3={'addressing_style': 'path'})
    )


# -----------------------
# Routes
# -----------------------
@app.route('/')
@login_required
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
@login_required
def list_buckets():
    try:
        client = get_s3_client()
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
@login_required
def delete_bucket(bucket):
    try:
        current_app.logger.info('Deleting bucket %s', bucket)
        client = get_s3_client()
        client.delete_bucket(Bucket=bucket)
        return jsonify({'message': f'Bucket {bucket} deleted'}), 200
    except ClientError as e:
        current_app.logger.info(e)
        abort(404 if 'NoSuchBucket' in str(e) else 500, description=str(e))


@app.route('/buckets', methods=['POST'])
@login_required
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
        client.create_bucket(Bucket=bucket_name, CreateBucketConfiguration=config,
                             ObjectLockEnabledForBucket=object_locking)
        return jsonify({'message': f'Bucket {bucket_name} created'}), 201
    except ClientError as e:
        current_app.logger.info(e)
        abort(409 if 'BucketAlreadyExists' in str(e) or "BucketAlreadyOwnedByYou" in str(e) else 500,
              description=str(e) + ":" + str(getattr(e, 'response', None)))


@app.route('/buckets/<bucket>/objects', methods=['POST'])
@login_required
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
@login_required
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
@login_required
def download_object(bucket, key):
    try:
        client = get_s3_client()
        response = client.get_object(Bucket=bucket, Key=key)
        return send_file(io.BytesIO(response['Body'].read()), as_attachment=True, download_name=key)
    except ClientError as e:
        current_app.logger.exception("Download failed")
        abort(404 if 'NoSuchKey' in str(e) else 500, description=str(e))


@app.route('/buckets/<bucket>/objects/<key>', methods=['DELETE'])
@login_required
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


from swiftclient.client import Connection

conn = Connection(
    authurl='http://localhost:5000/v3',
    user='swift',
    key='testing',
    os_options={'project_name': 'service', 'user_domain_name': 'Default', 'project_domain_name': 'Default'},
    auth_version='3'
)

# lister containers
containers = conn.get_account()[1]
print([c['name'] for c in containers])


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





if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=3001)
