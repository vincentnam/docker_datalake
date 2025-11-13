



# app.py - API REST Flask pour proxy S3 (Swift compat)
from functools import wraps
from flask import Flask, request, jsonify, send_file, abort, g, session, redirect, url_for, current_app
from flask_cors import CORS
import boto3
from botocore.exceptions import ClientError
import io
from datetime import datetime
from flask_oidc import OpenIDConnect
import os
import requests
from dotenv import load_dotenv

from keycloak import KeycloakOpenID
load_dotenv()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        username = request.headers.get("X-Username") or request.headers.get("Username")
        password = request.headers.get("X-Password") or request.headers.get("Password")

        token = None

        # === CAS 1 : Token Bearer ===
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

            try:
                # Validation automatique du token
                userinfo = keycloak_openid.userinfo(token)
                g.user = {
                    "id": userinfo.get("sub"),
                    "username": userinfo.get("preferred_username"),
                    "email": userinfo.get("email"),
                    "roles": userinfo.get("realm_access", {}).get("roles", []),
                    "source": "token"
                }
                return f(*args, **kwargs)
            except Exception as e:
                current_app.logger.warning(f"Token invalide: {e}")
                return jsonify({"error": "Token invalide ou expiré"}), 401

        # === CAS 2 : Username + Password dans headers ===
        elif username and password:
            try:
                # Obtention du token via Keycloak
                token_data = keycloak_openid.token(
                    username=username,
                    password=password,
                    grant_type=["password"]
                )
                access_token = token_data["access_token"]

                # Validation + userinfo
                userinfo = keycloak_openid.userinfo(access_token)
                g.user = {
                    "id": userinfo.get("sub"),
                    "username": userinfo.get("preferred_username"),
                    "email": userinfo.get("email"),
                    "roles": userinfo.get("realm_access", {}).get("roles", []),
                    "source": "credentials",
                    "access_token": access_token  # optionnel
                }
                return f(*args, **kwargs)
            except Exception as e:
                current_app.logger.warning(f"Échec login: {e}")
                return jsonify({"error": "Identifiants incorrects"}), 401

        # === AUCUN MOYEN D'AUTH ===
        else:
            return jsonify({
                "error": "Authentification requise",
                "hint": "Bearer token ou X-Username + X-Password"
            }), 401

    return decorated_function
app = Flask(__name__)


keycloak_openid = KeycloakOpenID(server_url=os.getenv("KEYCLOAK_ISSUER"),
                                 client_id=os.getenv("KEYCLOAK_CLIENT_ID"),
                                 realm_name=os.getenv('KEYCLOAK_REALM'),
                                 client_secret_key=os.getenv('KEYCLOAK_CLIENT_SECRET'))



CORS(app, resources={r"/buckets": {"origins": "*", "methods": ["GET", "POST", "OPTIONS"]},
                     r"/buckets/*": {"origins": "*", "methods": ["GET", "POST", "DELETE", "OPTIONS"]}})


app.config['DEBUG'] = True
# Config S3 client (Swift endpoint)
s3_client = boto3.client(
    's3',
    endpoint_url='http://10.5.10.1:8080',  # Swift endpoint - management node
    aws_access_key_id='test:tester',  # Temp auth Swift
    aws_secret_access_key='testing',
    region_name='us-east-1',
    config=boto3.session.Config(signature_version='s3v4', s3={'addressing_style': 'path'})
)


@app.route('/api/login', methods=['GET'])

def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    # if not username or not password:
    #     return jsonify({'error': 'Username and password required'}), 400

    # payload = {
    #     'grant_type': 'password',
    #     'client_id': "REST_API",
    #     'client_secret': "JDlkD6DktrbirbiclJPksQ4wlAabEknT",
    #     'username': "test",
    #     'password': "test1",
    #     'scope': 'openid profile email'
    # }



    token = keycloak_openid.token("test1","test")
    return token
    # response = requests.post("http://neosso.univ-tlse3.fr/realms/MIDOC/protocol/openid-connect/token", data=payload)
    # if response.status_code == 200:
    #     return jsonify(response.json())
    # else:
    #     app.logger.info(response.json())
    #     return jsonify({'error': 'Authentication failed'}), response.status_code


@app.route('/')
@login_required
def index():
    # g.user est rempli par le décorateur @login_required
    app.logger.info(f"Utilisateur connecté : {g.user}")

    # Vérifie que l'utilisateur est bien authentifié
    if g.user and g.user.get("username"):
        return f'Bienvenue {g.user["username"]} ! (email: {g.user.get("email", "N/A")})'
    else:
        return 'Utilisateur inconnu (authentification échouée)', 500


@app.route('/buckets', methods=['GET'])
def list_buckets():
    try:
        response = s3_client.list_buckets()  # Appel à boto3 pour lister les buckets
        app.logger.info(response)  # Log de la réponse complète pour debug

        # Extraction enrichie des buckets avec nom et date de création (convertie en ISO pour JSON)
        buckets = [
            {
                'Name': b['Name'],
                'CreationDate': b['CreationDate'].isoformat() if 'CreationDate' in b else None
            }
            for b in response.get('Buckets', [])  # Utilise get() pour éviter KeyError si absent
        ]

        # Extraction de l'owner avec display_name et ID
        owner = {
            'DisplayName': response.get('Owner', {}).get('DisplayName'),
            'ID': response.get('Owner', {}).get('ID')
        } if 'Owner' in response else None

        # Retour JSON enrichi : buckets avec détails, et owner
        return jsonify({'buckets': buckets, 'owner': owner})
    except ClientError as e:
        app.logger.info(e)  # Log de l'erreur pour traçabilité
        abort(500, description=str(e))  # Gestion d'erreur standard

@app.route('/buckets/<bucket>', methods=['DELETE'])
def delete_bucket(bucket):
    try:
        app.logger.info('Deleting bucket {}'.format(bucket))
        s3_client.delete_bucket(Bucket=bucket)

        return jsonify({'message': f'Bucket {bucket} deleted'}), 200
    except ClientError as e:
        app.logger.info(e)
        abort(404 if 'NoSuchBucket' in str(e) else 500, description=str(e))
@app.route('/buckets', methods=['POST'])
def create_bucket():
    data = request.json

    app.logger.info(data)

    app.logger.info(request)
    bucket_name = data.get('name')
    region = data.get('region', 'us-east-1')
    object_locking = bool(data.get('objectLocking', False))  # Convert to bool
    if not bucket_name:
        abort(400, description='Bucket name required')
    try:
        config = {'LocationConstraint': region} if region else {}
        s3_client.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration=config,
            ObjectLockEnabledForBucket=object_locking
        )
        return jsonify({'message': f'Bucket {bucket_name} created'}), 201
    except ClientError as e:
        app.logger.info(e)
        app.logger.info(e.response['Error']['Message'])

        abort(409 if 'BucketAlreadyExists' in str(e) or "BucketAlreadyOwnedByYou" in str(e) else 500, description=str(e) + ":" + str(e.response))



# @app.route('/buckets/<bucket>/objects', methods=['GET'])
# def list_objects(bucket):
#     prefix = request.args.get('prefix', '')
#     try:
#         response = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)
#         objects = [{'key': obj['Key'], 'size': obj['Size']} for obj in response.get('Contents', [])]
#         return jsonify({'objects': objects})
#     except ClientError as e:
#         app.logger.info(e)
#         abort(404 if 'NoSuchBucket' in str(e) else 500, description=str(e))
@app.route('/buckets/<bucket>/objects', methods=['POST'])
def upload_object(bucket):
    if 'file' not in request.files:
        abort(400, description='No file uploaded')
    file = request.files['file']
    key = request.form.get('key', file.filename)
    content_type = request.form.get('contentType', 'application/octet-stream')
    creation_date = request.form.get('creationDate', datetime.now().isoformat())  # Fallback UTC

    try:
        s3_client.put_object(
            Bucket=bucket,
            Key=key,
            Body=file.stream.read(),
            ContentType=content_type,
            Metadata={'CreationDate': creation_date}  # Stockage en metadata
        )
        return jsonify({'message': f'Object {key} uploaded'}), 201
    except ClientError as e:
        app.logger.info(e)
        abort(500, description=str(e))


@app.route('/buckets/<bucket>/objects', methods=['GET'])
def list_objects(bucket):
    prefix = request.args.get('prefix', '')
    delimiter = request.args.get('delimiter', '/')
    try:
        response = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix, Delimiter=delimiter)

        objects = []
        for obj in response.get('Contents', []):
            key = obj['Key']
            try:
                head_response = s3_client.head_object(Bucket=bucket, Key=key)

                obj_data = {
                    'key': key,
                    'size': obj['Size'],
                    'lastModified': obj['LastModified'].isoformat() if 'LastModified' in obj else None,
                    'eTag': obj.get('ETag', head_response.get('ETag')),
                    'storageClass': obj.get('StorageClass', head_response.get('StorageClass', 'STANDARD'))
                }

                metadata = {
                    'contentType': head_response.get('ContentType', 'application/octet-stream'),
                    'contentLength': head_response.get('ContentLength', obj['Size']),
                    'cacheControl': head_response.get('CacheControl'),
                    'contentDisposition': head_response.get('ContentDisposition'),
                    'contentEncoding': head_response.get('ContentEncoding'),
                    'contentLanguage': head_response.get('ContentLanguage'),
                    'expires': head_response.get('Expires'),
                    'serverSideEncryption': head_response.get('ServerSideEncryptionAlgorithm'),
                    'ssekmsKeyId': head_response.get('SSEKMSKeyId'),
                    'metadata': head_response.get('Metadata', {}),  # User metadata incl. CreationDate
                    'versionId': head_response.get('VersionId'),
                    'websiteRedirectLocation': head_response.get('WebsiteRedirectLocation'),
                    'objectLockMode': head_response.get('ObjectLockMode'),
                    'objectLockLegalHoldStatus': head_response.get('ObjectLockLegalHoldStatus'),
                    'objectLockRetainUntilDate': head_response.get('ObjectLockRetainUntilDate')
                }

                full_obj = {**obj_data, **{k: v for k, v in metadata.items() if v is not None}}

            except ClientError as head_err:
                app.logger.warning(f"HEAD failed for {key}: {head_err}")
                full_obj = {
                    'key': key,
                    'size': obj['Size'],
                    'lastModified': obj['LastModified'].isoformat() if 'LastModified' in obj else None,
                    'eTag': obj.get('ETag'),
                    'storageClass': obj.get('StorageClass', 'STANDARD'),
                    'contentType': 'application/octet-stream'
                }

            objects.append(full_obj)

        app.logger.info(objects)
        prefixes = [{'prefix': p['Prefix']} for p in response.get('CommonPrefixes', [])]
        return jsonify({'objects': objects, 'prefixes': prefixes})
    except ClientError as e:
        app.logger.info(e)
        abort(404 if 'NoSuchBucket' in str(e) else 500, description=str(e))
@app.route('/buckets/<bucket>/objects/<key>', methods=['GET'])
def download_object(bucket, key):
    try:
        response = s3_client.get_object(Bucket=bucket, Key=key)
        return send_file(io.BytesIO(response['Body'].read()), as_attachment=True, download_name=key)
    except ClientError as e:
        app.logger.info(e)
        abort(404 if 'NoSuchKey' in str(e) else 500, description=str(e))

@app.route('/buckets/<bucket>/objects/<key>', methods=['DELETE'])
def delete_object(bucket, key):
    try:
        s3_client.delete_object(Bucket=bucket, Key=key)
        return jsonify({'message': f'Object {key} deleted'})
    except ClientError as e:
        app.logger.info(e)
        abort(404 if 'NoSuchKey' in str(e) else 500, description=str(e))

if __name__ == '__main__':
    app.run(debug=True, port=5000)