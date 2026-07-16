import os
import sys

c = get_config()

sys.path.insert(0, "/srv/jupyterhub")

# --- 1. URL et Réseau ---
c.JupyterHub.base_url = '/hub/'
c.JupyterHub.bind_url = 'http://:8000' 

# --- 2. Docker Spawner ---
c.JupyterHub.spawner_class = "dockerspawner.DockerSpawner"
c.DockerSpawner.image = os.environ.get("DOCKER_NOTEBOOK_IMAGE", "jupyter/base-notebook")
c.DockerSpawner.network_name = os.environ.get("DOCKER_NETWORK_NAME", "jupyter-net")
c.DockerSpawner.use_internal_ip = True


c.JupyterHub.hub_connect_ip = '10.5.100.1'

c.DockerSpawner.notebook_dir = "/home/jovyan/work"
c.DockerSpawner.volumes = {"jupyterhub-user-{username}": "/home/jovyan/work"}
c.DockerSpawner.remove = True
c.DockerSpawner.debug = True

# --- 3. Base de données ---
c.JupyterHub.cookie_secret_file = "/data/jupyterhub_cookie_secret"
c.JupyterHub.db_url = "sqlite:////data/jupyterhub.sqlite"

# --- 4. Authentification ---
from datalake_authenticator import FlaskLocalAuthenticator

c.JupyterHub.authenticator_class = FlaskLocalAuthenticator
c.JupyterHub.template_paths = ["/srv/jupyterhub/templates"]
c.FlaskLocalAuthenticator.flask_base_url = os.environ.get(
    "FLASK_INTERNAL_URL", "http://flask-app:5000"
)
c.Authenticator.admin_users = {os.environ.get("JUPYTERHUB_ADMIN", "admin")}
c.Authenticator.allow_all = True
