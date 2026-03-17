
from datalake_objectstoreclient import ObjectStorageClient
from datalake_authclient import KeystoneClient

from datetime import datetime

class AuthenticationError(ValueError):
    """Erreur d'authentification / paramètres invalides pour le backend."""
    pass



class SwiftStorage(ObjectStorageClient):



    def __init__(self, authentication_client=None, user=None,password=None, token=None, preauthurl=None, project_name=None, user_domain_name="Default",project_domain_name="Default",current_app = None, **kwargs):
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
        assert isinstance(authentication_client, KeystoneClient), "Wrong authentication system : need Openstack Keystone authentication system with Openstack Swift"

        if token is not None and preauthurl is not None:
            #TODO : BUG : Log avec un token ne permet pas de récupérer les données pour accéder à swift a priori : token retourne pas les buckets / user-password retourner la liste des buckets
            self.client = swiftclient.Connection(preauthurl=preauthurl,
                                          preauthtoken=token,
                                          os_options={'project_name': project_name, 'user_domain_name': user_domain_name, 'project_domain_name': project_domain_name},
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
        else :
            if user is not None and password is not None:
                try:
                    self.client = swiftclient.Connection(authentication_client.KEYSTONE_URL,
                                                         user,
                                                         password,

                                                         os_options={'project_name': project_name,
                                                                      'user_domain_name': user_domain_name,
                                                                      'project_domain_name': project_domain_name},
                                                         auth_version="3")
                except Exception as e :
                    self.current_app.logger.warning(e)

            else :

                raise AuthenticationError("User / Password or Token missing ")






    def list_buckets(self):
        return  self.client.get_account()

    def create_bucket(self, name, *args, **kwargs):
        return self.client.put_container(name)

    def delete_bucket(self, name, *args, **kwargs):
        return self.client.delete_container(name)

    def list_objects(self, bucket, prefix="", delimiter="/", *args, **kwargs):
        return self.client.get_container(bucket, prefix=prefix, delimiter=delimiter)

    def upload_object(self, bucket, key, file_obj, content_type=None, metadata=None, *args, **kwargs):
        return self.client.put_object(bucket, file_obj, content_type, metadata=None, name=key,
                                      headers={
                                            'X-Object-Meta-Date-Added': datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                                        }
                                      )

    def download_object(self, bucket, key, *args, **kwargs):
        return self.client.get_object(container=bucket, obj=key)

    def delete_object(self, bucket, key, *args, **kwargs):
        return self.client.delete_object(container=bucket, obj=key)


    def head_object(self, bucket, key, *args, **kwargs):
        return self.client.head_object(container=bucket, obj=key)