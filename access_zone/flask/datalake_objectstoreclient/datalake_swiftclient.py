from datalake_authclient import KeystoneClient
from datetime import datetime

from datalake_objectstoreclient import ObjectStorageClient


class AuthenticationError(ValueError):
    """Erreur d'authentification / paramètres invalides pour le backend."""
    pass


class SwiftStorage(ObjectStorageClient):

    def __init__(self, authentication_client=None, user=None, password=None, token=None, preauthurl=None,
                 project_name=None, user_domain_name="Default", project_domain_name="Default", current_app=None,
                 **kwargs):
        self.current_app = current_app
        from swiftclient import client as swiftclient
        # TODO: ADD : Logger level for debug
        # self.current_app.logger.info("┌─ Swift client initialization ───────────────┐")
        # self.current_app.logger.info(f"│  URL               : {authentication_client.KEYSTONE_URL} │")
        # self.current_app.logger.info(f"│  user               : {user or '<none>':<25} │")
        # self.current_app.logger.info(f"│  password           : {password or '<none>':<25} │")
        # self.current_app.logger.info(f"│  token              : {token or '<none>':<10} │")
        # self.current_app.logger.info(f"│  project_name       : {project_name or '<none>':<25} │")
        # self.current_app.logger.info(f"│  domain names       : {user_domain_name} / {project_domain_name}")
        # self.current_app.logger.info(f"│  current_app        : {bool(current_app)}")
        # self.current_app.logger.info("└─────────────────────────────────────────────────────────┘")
        # self.current_app.logger.info( str(user),  str(password),  str(token),  str(project_name))

        # self.current_app.logger.info(authentication_client)
        assert isinstance(authentication_client,
                          KeystoneClient), "Wrong authentication system : need Openstack Keystone authentication system with Openstack Swift"

        if token is not None and preauthurl is not None:
            # TODO : BUG : Log avec un token ne permet pas de récupérer les données pour accéder à swift a priori : token retourne pas les buckets / user-password retourner la liste des buckets
            self.client = swiftclient.Connection(preauthurl=preauthurl,
                                                 preauthtoken=token,
                                                 os_options={'project_name': project_name,
                                                             'user_domain_name': user_domain_name,
                                                             'project_domain_name': project_domain_name},
                                                 auth_version="3")
            try:
                account, containers = self.client.get_account()
                # self.current_app.logger.info("┌─ Swift client initialization ───────────────┐")
                # self.current_app.logger.info("Authentification réussie ✓")
                # self.current_app.logger.info(f"  Account   : {account}")
                # self.current_app.logger.info(f"  Token     : {self.client.token[:20]}... (tronqué)")
                # self.current_app.logger.info(f"  Containers: {len(containers)} trouvés ({str(containers)})")
                # self.current_app.logger.info("└─────────────────────────────────────────────────────────┘")
                # return self.client
            except swiftclient.ClientException as e:
                self.current_app.logger.info("Authentication error :", e)
                raise
        else:
            if user is not None and password is not None:
                try:
                    self.client = swiftclient.Connection(authentication_client.KEYSTONE_URL,
                                                         user,
                                                         password,

                                                         os_options={'project_name': project_name,
                                                                     'user_domain_name': user_domain_name,
                                                                     'project_domain_name': project_domain_name},
                                                         auth_version="3")
                except Exception as e:
                    self.current_app.logger.warning(e)
            else:

                raise AuthenticationError("User / Password or Token missing ")

    def list_buckets(self):
        headers, containers = self.client.get_account()
        formatted_buckets = [
            {
                'Name': c['name'],
                'CreationDate': "#TODO",  # Swift ne le donne pas ici
                'Count': c.get('count', 0),
                'Bytes': c.get('bytes', 0)
            }
            for c in containers
        ]
        return {
            'Buckets': formatted_buckets,
            'Owner': "#TODO"  # Optionnel pour Swift
        }

    def create_bucket(self, name, *args, **kwargs):
        return self.client.put_container(name)

    def delete_bucket(self, name, *args, **kwargs):
        return self.client.delete_container(name)

    # def list_objects(self, bucket, prefix="", delimiter="/", *args, **kwargs):
    #     return self.client.get_container(bucket, prefix=prefix, delimiter=delimiter)

    def list_objects(self, bucket, prefix="", delimiter="/", *args, **kwargs):
        # 1. Récupération de la liste brute
        headers, items = self.client.get_container(bucket, prefix=prefix, delimiter=delimiter)

        objects = []
        prefixes = []

        for item in items:
            if 'subdir' in item:
                prefixes.append({'prefix': item['subdir']})
                continue

            try:
                # 2. Récupération des headers complets de l'objet
                # head_object renvoie un dictionnaire des headers HTTP
                full_headers = self.head_object(bucket, item['name'])

                # 3. On extrait les métadonnées sans modifier les clés
                # On garde 'X-Object-Meta-Date-Added' tel quel
                custom_metadata = {
                    k: v for k, v in full_headers.items()
                    if k.lower().startswith('x-object-meta-')
                }

                # 4. On cherche notre date pour le champ standardisé (insensible à la casse pour la recherche)
                # On cherche dans les clés d'origine pour extraire la valeur
                creation_date = next((v for k, v in custom_metadata.items() if k.lower() == 'x-object-meta-date-added'),
                                     None)

            except Exception as e:
                self.current_app.logger.warning(f"Could not get head for {item['name']}: {e}")
                custom_metadata = {}
                creation_date = None

            objects.append({
                'key': item.get('name'),
                'size': item.get('bytes'),
                'lastModified': item.get('last_modified'),
                'creationDate': creation_date,
                'eTag': item.get('hash'),
                'contentType': item.get('content_type', 'application/octet-stream'),
                'storageClass': 'STANDARD',
                'metadata': custom_metadata  # Clés brutes conservées
            })

        return {
            'objects': objects,
            'prefixes': prefixes
        }

    def upload_object(self, bucket, key, file_obj, content_type=None, metadata=None, *args, **kwargs):

        return self.client.put_object(
            container=bucket,
            obj=key,
            contents=file_obj,
            content_type=content_type,
            headers={'X-Object-Meta-Date-Added': datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
        )

    def download_object(self, bucket, key, *args, **kwargs):
        headers, body = self.client.get_object(container=bucket, obj=key)
        return body

    def delete_object(self, bucket, key, *args, **kwargs):
        return self.client.delete_object(container=bucket, obj=key)

    def head_object(self, bucket, key, *args, **kwargs):
        return self.client.head_object(container=bucket, obj=key)

    def head_bucket(self, name, *args, **kwargs):
        return self.client.head_container(name)