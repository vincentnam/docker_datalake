import os

from .datalake_authclient import (
    AuthenticationBackendError,
    AuthenticationClient,
    AuthenticationRejected,
)
from .datalake_keystone import KeystoneClient
from .datalake_openstackclient import OpenstackSDKAuthClient


def get_auth(backend: str = None) -> AuthenticationClient:
    """Factory : retourne le bon client selon la variable d'environnement"""
    backend = (
        backend or os.getenv("AUTHENTICATION_BACKEND", "keystone")
    ).lower()

    if backend == "keystone":
        return KeystoneClient()
    if backend == "openstack":
        return OpenstackSDKAuthClient()

    raise ValueError(f"Backend d'authentification inconnu : {backend}")

__all__ = [
    "AuthenticationBackendError",
    "AuthenticationClient",
    "AuthenticationRejected",
    "KeystoneClient",
    "OpenstackSDKAuthClient",
    "get_auth",
]
