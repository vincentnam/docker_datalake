from abc import ABC, abstractmethod

class ObjectStorageClient(ABC):

    @abstractmethod
    def __init__(self, authentication_client=None, user=None,password=None, token=None, *args, **kwargs):
        pass
    # === API UNIFIÉE (même signature partout) ===
    @abstractmethod
    def list_buckets(self, *args, **kwargs):
        pass

    @abstractmethod
    def create_bucket(self, name, *args, **kwargs):
        pass

    @abstractmethod
    def delete_bucket(self, name, *args, **kwargs):
        pass

    @abstractmethod
    def list_objects(self, bucket, prefix="", delimiter="/", *args, **kwargs):
        pass

    @abstractmethod
    def upload_object(self, bucket, key, file_obj, content_type=None, metadata=None, *args, **kwargs):
        pass

    @abstractmethod
    def download_object(self, bucket, key, *args, **kwargs):
        pass

    @abstractmethod
    def delete_object(self, bucket, key, *args, **kwargs):
        pass

    @abstractmethod
    def head_object(self, bucket, key, *args, **kwargs):
        pass