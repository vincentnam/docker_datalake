from datalake_objectstoreclient import ObjectStorageClient


class S3Storage(ObjectStorageClient):
    def __init__(self,user=None, password=None, token=None):
        pass
    def create_bucket(self, name, region="us-east-1", object_locking=False):
        pass

    def delete_bucket(self, name):
        pass

    def list_objects(self, bucket, prefix="", delimiter="/"):
        pass

    def upload_object(self, bucket, key, file_obj, content_type=None, metadata=None):
        pass

    def download_object(self, bucket, key):
        pass

    def delete_object(self, bucket, key):
        pass

    def head_object(self, bucket, key):
        pass

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
