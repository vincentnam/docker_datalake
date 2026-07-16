from abc import ABC, abstractmethod


class AuthenticationRejected(Exception):
    """Les identifiants fournis ont été refusés."""


class AuthenticationBackendError(Exception):
    """Le backend d'identité n'a pas pu terminer l'authentification."""


class AuthenticationClient(ABC):
    @abstractmethod
    def authenticate_credentials(
        self,
        username,
        password,
        project_name=None,
        project_id=None,
    ):
        """Valide les identifiants et retourne un utilisateur normalisé."""
        raise NotImplementedError

    @abstractmethod
    def login_required(self, f):
        """Doit retourner une fonction wrapper
        Cette fonction doit remplir g (le contexte de flask)
        Exemple (keystone.py):
            g.user = {
                "id": access_info.user_id,
                "username": access_info.username,
                "roles": access_info.role_names or [],
                "project_id": access_info.project_id,
                "project_name": access_info.project_name,
                "source": "credentials",
                "access_token": access_token,
                "projects": [],
                "ec2_credentials": None
                }
        """
        raise NotImplementedError
