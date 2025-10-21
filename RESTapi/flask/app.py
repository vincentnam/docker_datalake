# from flask import Flask, request, jsonify, send_file, abort, session
# from flask_cors import CORS
# import boto3
# from botocore.exceptions import ClientError
# from botocore.config import Config
# import io
# import jwt  # pip install pyjwt
# from functools import wraps
#
# app = Flask(__name__)
# app.secret_key = 'your-secret-key'  # Changez pour prod
# CORS(app)
#
#
# def get_s3_client_from_request():
#     """Crée client S3 par requête basé sur creds user (ex. JWT header)"""
#     auth_header = request.headers.get('Authorization')
#     if not auth_header:
#         abort(401, description='Auth required')
#
#     try:
#         # Ex. JWT decode (ajustez secret/algorithme)
#         token = auth_header.split(' ')[1]
#         payload = jwt.decode(token, 'your-jwt-secret', algorithms=['HS256'])
#         access_key = payload.get('access_key')  # Ex. test:tester
#         secret_key = payload.get('secret_key')  # testing
#     except jwt.InvalidTokenError:
#         abort(401, description='Invalid token')
#
#     return boto3.client(
#         's3',
#         endpoint_url='http://localhost:8080',
#         aws_access_key_id=access_key,
#         aws_secret_access_key=secret_key,
#         region_name='auto',
#         config=Config(signature_version='s3v4', s3={'addressing_style': 'path'})
#     )
#
#
# def require_auth(f):
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         session['user_id'] = request.headers.get('User-ID', 'default')  # Stocke session Flask si besoin
#         return f(*args, **kwargs)
#
#     return decorated
#
#
# @app.route('/buckets', methods=['GET'])
# @require_auth
# def list_buckets():
#     s3 = get_s3_client_from_request()
#     try:
#         response = s3.list_buckets()
#         buckets = [{'name': b['Name']} for b in response['Buckets']]
#         return jsonify({'buckets': buckets})
#     except ClientError as e:
#         abort(500, description=str(e))
#
#
# @app.route('/buckets', methods=['POST'])
# @require_auth
# def create_bucket():
#     bucket_name = request.json.get('name')
#     if not bucket_name:
#         abort(400, description='Bucket name required')
#     s3 = get_s3_client_from_request()
#     try:
#         s3.create_bucket(Bucket=bucket_name)
#         return jsonify({'message': f'Bucket {bucket_name} created'}), 201
#     except ClientError as e:
#         abort(409 if 'BucketAlreadyExists' in str(e) else 500, description=str(e))
#
#
# @app.route('/buckets/<bucket>/objects', methods=['GET'])
# @require_auth
# def list_objects(bucket):
#     prefix = request.args.get('prefix', '')
#     s3 = get_s3_client_from_request()
#     try:
#         response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
#         objects = [{'key': obj['Key'], 'size': obj['Size']} for obj in response.get('Contents', [])]
#         return jsonify({'objects': objects})
#     except ClientError as e:
#         abort(404 if 'NoSuchBucket' in str(e) else 500, description=str(e))
#
#
# @app.route('/buckets/<bucket>/objects', methods=['POST'])
# @require_auth
# def upload_object(bucket):
#     if 'file' not in request.files:
#         abort(400, description='No file uploaded')
#     file = request.files['file']
#     key = request.form.get('key', file.filename)
#     s3 = get_s3_client_from_request()
#     try:
#         s3.put_object(Bucket=bucket, Key=key, Body=file.stream.read())
#         return jsonify({'message': f'Object {key} uploaded'}), 201
#     except ClientError as e:
#         abort(500, description=str(e))
#
#
# @app.route('/buckets/<bucket>/objects/<key>', methods=['GET'])
# @require_auth
# def download_object(bucket, key):
#     s3 = get_s3_client_from_request()
#     try:
#         response = s3.get_object(Bucket=bucket, Key=key)
#         return send_file(io.BytesIO(response['Body'].read()), as_attachment=True, download_name=key)
#     except ClientError as e:
#         abort(404 if 'NoSuchKey' in str(e) else 500, description=str(e))
#
#
# @app.route('/buckets/<bucket>/objects/<key>', methods=['DELETE'])
# @require_auth
# def delete_object(bucket, key):
#     s3 = get_s3_client_from_request()
#     try:
#         s3.delete_object(Bucket=bucket, Key=key)
#         return jsonify({'message': f'Object {key} deleted'})
#     except ClientError as e:
#         abort(404 if 'NoSuchKey' in str(e) else 500, description=str(e))
#
#
# if __name__ == '__main__':
#     app.run(debug=True, port=5000)




# app.py - API REST Flask pour proxy S3 (Swift compat)
from flask import Flask, request, jsonify, send_file, abort
from flask_cors import CORS
import boto3
from botocore.exceptions import ClientError
import io
import os

app = Flask(__name__)
CORS(app)  # Pour React frontend

# Config S3 client (Swift endpoint)
s3_client = boto3.client(
    's3',
    endpoint_url='http://10.5.10.1:8080',  # Swift SAIO endpoint
    aws_access_key_id='test:tester',  # Temp auth Swift
    aws_secret_access_key='testing',
    region_name='us-east-1',
    config=boto3.session.Config(signature_version='s3v4', s3={'addressing_style': 'path'})
)

@app.route('/buckets', methods=['GET'])
def list_buckets():
    try:
        app.logger.info('COUCOU\nSA VA ?\n')
        response = s3_client.list_buckets()
        buckets = [{'name': b['Name']} for b in response['Buckets']]
        return jsonify({'buckets': buckets})
    except ClientError as e:

        abort(500, description=str(e))

@app.route('/buckets', methods=['POST'])
def create_bucket():
    bucket_name = request.json.get('name')
    if not bucket_name:
        abort(400, description='Bucket name required')
    try:
        s3_client.create_bucket(Bucket=bucket_name)
        return jsonify({'message': f'Bucket {bucket_name} created'}), 201
    except ClientError as e:
        abort(409 if 'BucketAlreadyExists' in str(e) else 500, description=str(e))

@app.route('/buckets/<bucket>/objects', methods=['GET'])
def list_objects(bucket):
    prefix = request.args.get('prefix', '')
    try:
        response = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)
        objects = [{'key': obj['Key'], 'size': obj['Size']} for obj in response.get('Contents', [])]
        return jsonify({'objects': objects})
    except ClientError as e:
        abort(404 if 'NoSuchBucket' in str(e) else 500, description=str(e))

@app.route('/buckets/<bucket>/objects', methods=['POST'])
def upload_object(bucket):
    if 'file' not in request.files:
        abort(400, description='No file uploaded')
    file = request.files['file']
    key = request.form.get('key', file.filename)
    try:
        s3_client.put_object(Bucket=bucket, Key=key, Body=file.stream.read())
        return jsonify({'message': f'Object {key} uploaded'}), 201
    except ClientError as e:
        abort(500, description=str(e))

@app.route('/buckets/<bucket>/objects/<key>', methods=['GET'])
def download_object(bucket, key):
    try:
        response = s3_client.get_object(Bucket=bucket, Key=key)
        return send_file(io.BytesIO(response['Body'].read()), as_attachment=True, download_name=key)
    except ClientError as e:
        abort(404 if 'NoSuchKey' in str(e) else 500, description=str(e))

@app.route('/buckets/<bucket>/objects/<key>', methods=['DELETE'])
def delete_object(bucket, key):
    try:
        s3_client.delete_object(Bucket=bucket, Key=key)
        return jsonify({'message': f'Object {key} deleted'})
    except ClientError as e:
        abort(404 if 'NoSuchKey' in str(e) else 500, description=str(e))

if __name__ == '__main__':
    app.run(debug=True, port=5000)