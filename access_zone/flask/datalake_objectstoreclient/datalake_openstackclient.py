import openstack
from datetime import datetime

from datalake_authclient import KeystoneClient, OpenstackSDKAuthClient
from datalake_objectstoreclient import ObjectStorageClient


class AuthenticationError(ValueError):
    """Erreur d'authentification / paramètres invalides pour le backend."""
    pass


class OpenstackSDKSwiftStorageClient(ObjectStorageClient):

    def __init__(self, authentication_client=None, user=None, password=None, token=None, preauthurl=None,
                 project_name=None, user_domain_name="Default", project_domain_name="Default", current_app=None,
                 **kwargs):
        self.current_app = current_app

        # Validation du client d'authentification
        assert isinstance(authentication_client, KeystoneClient) or isinstance(authentication_client,
                                                                               OpenstackSDKAuthClient), "Wrong authentication system : need Openstack Keystone authentication system with Openstack Swift"

        if token is not None and preauthurl is not None:
            try:
                # Connexion via SDK avec token et surcharge de l'URL Swift (preauthurl)
                self.conn = openstack.connect(
                    auth_url=authentication_client.KEYSTONE_URL,
                    token=token,
                    project_name=project_name,
                    project_domain_name=project_domain_name,
                    user_domain_name=user_domain_name,
                    object_store_endpoint_override=preauthurl
                )
                # Validation de la connexion en récupérant les métadonnées du compte (équivalent de get_account)
                self.conn.object_store.get_account_metadata()
            except openstack.exceptions.SDKException as e:
                self.current_app.logger.info(f"Authentication error: {e}")
                raise
        else:
            if user is not None and password is not None:
                try:
                    # Connexion classique via username/password
                    self.conn = openstack.connect(
                        auth_url=authentication_client.KEYSTONE_URL,
                        username=user,
                        password=password,
                        project_name=project_name,
                        user_domain_name=user_domain_name,
                        project_domain_name=project_domain_name
                    )
                except Exception as e:
                    self.current_app.logger.warning(e)
                    raise AuthenticationError("Authentication failed with provided credentials.")
            else:
                raise AuthenticationError("User / Password or Token missing ")

    def list_buckets(self):
        formatted_buckets = []
        # Le SDK gère la pagination automatiquement
        for c in self.conn.object_store.containers():
            formatted_buckets.append({
                'Name': c.name,
                'CreationDate': "#TODO",  # Swift ne le donne pas
                'Count': c.object_count or 0,
                'Bytes': c.bytes_used or 0
            })

        return {
            'Buckets': formatted_buckets,
            'Owner': "#TODO"  # Optionnel pour Swift
        }

    def create_bucket(self, name, *args, **kwargs):
        return self.conn.object_store.create_container(name=name)

    def delete_bucket(self, name, *args, **kwargs):
        # Openstack SDK retourne None si succès
        self.conn.object_store.delete_container(name)
        return True

    def list_objects(self, bucket, prefix="", delimiter="/", *args, **kwargs):
        objects = []
        prefixes = []

        # Récupération de la liste brute
        items = self.conn.object_store.objects(bucket, prefix=prefix, delimiter=delimiter)

        for item in items:
            # En OpenStack SDK, si on utilise un delimiter, les "dossiers"
            # apparaissent souvent avec une taille nulle et finissant par le delimiter.
            if item.name.endswith(delimiter) and item.bytes is None:
                prefixes.append({'prefix': item.name})
                continue

            try:
                # Récupération des métadonnées spécifiques de l'objet via une requête HEAD
                meta_obj = self.conn.object_store.get_object_metadata(item.name, container=bucket)

                # Le SDK OpenStack enlève automatiquement "X-Object-Meta-" des clés de metadata
                # On les recrée pour conserver la rétrocompatibilité de votre fonction
                custom_metadata = {
                    f"X-Object-Meta-{k}": v for k, v in meta_obj.metadata.items()
                }

                # On cherche notre date de création (insensible à la casse)
                creation_date = next((v for k, v in meta_obj.metadata.items() if k.lower() == 'date-added'), None)

            except Exception as e:
                self.current_app.logger.warning(f"Could not get head for {item.name}: {e}")
                custom_metadata = {}
                creation_date = None

            objects.append({
                'key': item.name,
                'size': item.bytes,
                'lastModified': item.last_modified_at,
                'creationDate': creation_date,
                'eTag': item.etag,
                'contentType': item.content_type or 'application/octet-stream',
                'storageClass': 'STANDARD',
                'metadata': custom_metadata  # Clés avec préfixe reconstituées
            })

        return {
            'objects': objects,
            'prefixes': prefixes
        }

    def upload_object(self, bucket, key, file_obj, content_type=None, metadata=None, *args, **kwargs):
        # Le SDK attend un dictionnaire `metadata` sans le préfixe X-Object-Meta- (il l'ajoute lui-même)
        meta = {'Date-Added': datetime.now().strftime("%d/%m/%Y %H:%M:%S")}

        if metadata:
            for k, v in metadata.items():
                clean_key = k[14:] if k.lower().startswith("x-object-meta-") else k
                meta[clean_key] = v

        return self.conn.object_store.upload_object(
            container=bucket,
            name=key,
            data=file_obj,
            content_type=content_type,
            metadata=meta
        )

    def download_object(self, bucket, key, *args, **kwargs):
        # get_object retourne directement le contenu en bytes
        return self.conn.object_store.get_object(key, container=bucket)

    def delete_object(self, bucket, key, *args, **kwargs):
        self.conn.object_store.delete_object(key, container=bucket)
        return True

    def head_object(self, bucket, key, *args, **kwargs):
        # Le SDK retourne un objet. On le convertit en dictionnaire semblable aux headers natifs
        obj = self.conn.object_store.get_object_metadata(key, container=bucket)

        headers = {
            'content-type': obj.content_type,
            'content-length': str(obj.bytes) if obj.bytes else '0',
            'etag': obj.etag
        }

        # Ajout des métadonnées avec le préfixe
        for k, v in obj.metadata.items():
            headers[f"x-object-meta-{k.lower()}"] = v

        return headers

    def head_bucket(self, name, *args, **kwargs):
        container = self.conn.object_store.get_container_metadata(name)

        return {
            'x-container-object-count': str(container.object_count),
            'x-container-bytes-used': str(container.bytes_used),
            'x-container-read': container.read_ACL,
            'x-container-write': container.write_ACL
        }