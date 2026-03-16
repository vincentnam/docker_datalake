from abc import ABC, abstractmethod

class AuthenticationClient(ABC):
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
