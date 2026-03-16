
from datalake_objectstoreclient import ObjectStorageClient
from datalake_authclient import KeystoneClient

from datetime import datetime

class AuthenticationError(ValueError):
    """Erreur d'authentification / paramètres invalides pour le backend."""
    pass



class SwiftStorage(ObjectStorageClient):



    def __init__(self, authentication_client=None, user=None,password=None, token=None, project_name=None, user_domain_name="Default",project_domaine_name="Default"):
        from swiftclient import client as swiftclient
        print(authentication_client)
        assert isinstance(authentication_client, KeystoneClient), "Wrong authentication system : need Openstack Keystone authentication system with Openstack Swift"

        if token is not None:
            self.client = swiftclient.Connection(authentication_client.KEYSTONE_URL,
                                          preauthtoken=token,
                                          os_options={'project_name': project_name, 'user_domain_name': user_domain_name, 'project_domain_name': project_domaine_name},
                                                     auth_version="3")
        else :
            if user is not None and password is not None:
                try:
                    self.client = swiftclient.Connection(authentication_client.KEYSTONE_URL,
                                                  user,
                                                  password,
                                                  os_options={'project_name': project_name,
                                                              'user_domain_name': user_domain_name,
                                                              'project_domain_name': project_domaine_name},
                                                  auth_version="3")
                except Exception as e :
                    pass
            else :
                raise AuthenticationError("User / Password or Token missing ")






    def list_buckets(self):
        return self.client.get_account()

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