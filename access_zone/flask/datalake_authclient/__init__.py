from .datalake_authclient  import AuthenticationClient
from .datalake_keystone  import KeystoneClient


def get_auth(backend: str = None,current_app=None) -> AuthenticationClient:
    """Factory : retourne le bon client selon la variable d'environnement"""
    import os
    backend = backend or os.getenv("AUTHENTICATION_BACKEND", "keystone").lower()
    if backend == "keystone" :
        return KeystoneClient(current_app=current_app)
    # elif backend == "swift":
        # return SwiftStorage()

    raise ValueError(f"Object storage backend inconnu : {backend}")

__all__ = ["KeystoneClient", "get_auth"]