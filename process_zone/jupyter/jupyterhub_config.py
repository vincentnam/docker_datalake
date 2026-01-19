import os

c = get_config()

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
c.JupyterHub.authenticator_class = "nativeauthenticator.NativeAuthenticator"
c.NativeAuthenticator.open_signup = True
c.Authenticator.allow_all = True
