from .datalake_objectstoreclient import ObjectStorageClient
from .datalake_s3client import  S3Storage
from .datalake_swiftclient import  SwiftStorage
from .datalake_openstackclient import OpenstackSDKSwiftStorageClient
def get_storage(backend: str = None, authentication_system=None, user=None, password=None, token=None,preauthurl=None, project_name=None, current_app=None) -> ObjectStorageClient:
    """Factory : retourne le bon client selon la variable d'environnement"""
    import os

    assert authentication_system is not None, "Error : authentication_system is None"

    backend = backend or os.getenv("OBJECT_STORAGE_BACKEND", "swift").lower()

    if backend == "swift":
        return SwiftStorage(authentication_system,user=user, password=password, token=token, preauthurl=preauthurl, project_name=project_name, current_app = current_app)
    elif backend == "swiftSDK":
        return OpenstackSDKSwiftStorageClient(authentication_system,user=user, password=password, token=token, preauthurl=preauthurl, project_name=project_name, current_app = current_app)
    # elif backend == "s3":
    #     return S3Storage(authentication_system,user=user, password=password, token=token, current_app = current_app)
    raise ValueError(f"Object storage system inconnu : {backend}")

__all__ = ["ObjectStorageClient", "S3Storage", "SwiftStorage", "get_storage"]