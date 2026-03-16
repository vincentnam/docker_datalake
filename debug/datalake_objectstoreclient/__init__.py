from .datalake_objectstoreclient import ObjectStorageClient
from .datalake_s3client import  S3Storage
from .datalake_swiftclient import  SwiftStorage

def get_storage(backend: str = None, authentication_system=None, user=None, password=None, token=None) -> ObjectStorageClient:
    """Factory : retourne le bon client selon la variable d'environnement"""
    import os
    print(authentication_system)
    assert authentication_system is not None, "Error : authentication_system is None"

    backend = backend or os.getenv("OBJECT_STORAGE_BACKEND", "swift").lower()
    print("OBJECT")
    print(backend)
    if backend == "s3":
        return S3Storage(authentication_system,user=user, password=password, token=token)
    elif backend == "swift":
        return SwiftStorage(authentication_system,user=user, password=password, token=token)
    raise ValueError(f"Authentication system inconnu : {backend}")

__all__ = ["ObjectStorageClient", "S3Storage", "SwiftStorage", "get_storage"]