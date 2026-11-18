# docker_datalake

A self-hosted data lake built on OpenStack components, automatically deployable with Docker Compose or Kubernetes (k3s).

## Architecture

| Zone             | Services                                                                                                                                  | Role                                                               |
|------------------|-------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------|
| Raw data zone    | Included: OpenStack Swift (proxy + storage nodes)                                                                                         | Store raw data, unmodified, at the lowest possible cost            |
| Access zone      | Included: Flask REST API (API gateway), React web GUI (user-friendly interface), OpenStack Horizon (admin dashboard)                      | Give access to the data lake services                              |
| Process zone     | Included: JupyterHub. Planned: Airflow (orchestration), Apache Spark and Spark Streaming (data streams)                                   | "Brain" of the lake: orchestration, data exploration, stream processing |
| Consumption zone | Planned: Kubernetes / Docker (not managed)                                                                                                | Deploy services that consume the data                              |
| Security zone    | Included: OpenStack Keystone + MariaDB (local IdP, mandatory for Swift), Keycloak (default external IdP), nginx reverse proxy (single entry point) | Manage authentication and access                                   |
| Govern zone      | Planned: MongoDB (metadata management)                                                                                                    | Data lifecycle management                                          |
| Other            | Memcached (data lake caching system)                                                                                                      |                                                                    |

## Requirements

### Docker Compose platform

- Linux host
- Docker, with the Compose v2 plugin ('docker compose')
- 'sudo' (not tested with the root account)
- GNU 'getopt'

### Kubernetes platform (k3s)

- Linux host, k3s node (the images are built and imported into k3s locally)
- Docker and 'sudo'
- 'kubectl' (comes with k3s)
- 'envsubst' (package 'gettext-base')
- GNU 'getopt' and 'git'
- 'xfsprogs' for XFS disks, or 'e2fsprogs' for ext4 disks
- systemd as PID 1
- 'curl' (k3s install)

### WSL (test and development only)

- Turn on systemd in '/etc/wsl.conf', then restart WSL from Windows with 'wsl --shutdown':

  ```ini
  [boot]
  systemd=true
  ```

- If you have a 'D:' drive (mounted at '/mnt/d'), see [Troubleshooting](#kubernetes-local-static-provisioner-stuck-in-createcontainererror).

## How does this repo work?

Each service has its own folder, grouped by zone. For example, OpenStack Swift lives in 'rawdata_zone/openstackSwift/'. Every service runs in containers, deployed with Docker Compose or Kubernetes. All settings (passwords, replicas, storage size, ports, etc.) come from a single file, 'conf.env'.

'start.sh' runs both platforms:

- **Build ('-b')** turns 'conf.env' into the configuration files of each service and builds the images.
- **Run ('-r')** starts the services.

### Docker Compose

1. 'create_conf.sh' writes each service's configuration files into its folder.
2. 'create_docker.sh' generates 'docker-compose_datalake.yml' from that configuration.
3. 'start.sh' builds the Keystone and JupyterHub images and initializes Swift.
4. With '-r', 'docker compose up' starts every service. Test mode ('-t') adds a Caddy reverse proxy. (Planned to be removed)

### Kubernetes (k3s)

Kubernetes manifests live in 'kubernetes/', with the same zone layout as the Docker Compose files.

'start.sh' is the single entry point: build, deployment, update and maintenance.

1. With '-b', 'disk_creation.sh' creates the local disks (XFS by default, see 'DISK_FS') of Swift, MariaDB and Keycloak and exposes them to the cluster as PersistentVolumes.
2. With '-b', 'start.sh' builds the Swift, Keystone, Flask and web GUI images and imports them into k3s.
3. With '-b', each service's 'create_conf.sh' generates its configuration (ConfigMaps and Secrets) from 'conf.env', and 'create_rings.sh' builds the Swift rings.
4. With '-r', 'start.sh' fills the variables of the manifests (image tag, replicas, storage size, configuration checksum) with 'envsubst' and applies them with 'kubectl apply'. Only the services whose configuration changed are restarted.


## Configuration

All settings live in 'conf.env', at the repository root. The Example column gives the full line to write in the file.

Change every 'ChangeMe' value and every password before deploying, and never commit a 'conf.env' with real secrets.

### OpenStack Keystone build (LOCI)

| Variable | Description | Example |
|---|---|---|
| 'OPENSTACK_RELEASE_VAR' | OpenStack release used to build Keystone and Horizon: the branch name of their repositories (see [releases.openstack.org](https://releases.openstack.org/)). | OPENSTACK_RELEASE_VAR="stable/2026.1" |
| 'BASE_DISTRO_VAR' | Base OS image of the Keystone build. | BASE_DISTRO_VAR="ubuntu:noble" |
| 'BASE_TAG_VAR' | Tag of the built Keystone image. Free to change. | BASE_TAG_VAR="ubuntu_noble" |
| 'OS_USERNAME' | Username of the Keystone admin account, used for bootstrap and admin operations. | OS_USERNAME="admin" |
| 'OS_PASSWORD' | Password of the Keystone admin account. Required, 12 characters or more. | OS_PASSWORD="ChangeMe_admin_password" |
| 'SWIFT_PASSWORD' | Password of the 'swift' service account in Keystone. Required, 12 characters or more. | SWIFT_PASSWORD="ChangeMe_swift_password" |

### Keystone database (MariaDB)

| Variable | Description | Example |
|---|---|---|
| 'MYSQL_ROOT_PASSWORD' | MariaDB root password. Used only inside the container, when the database is provisioned. | MYSQL_ROOT_PASSWORD="ChangeMe_root_password" |
| 'MYSQL_DATABASE' | Name of the Keystone database. | MYSQL_DATABASE="keystone" |
| 'MYSQL_USER' | MariaDB user owned by Keystone. | MYSQL_USER="keystone" |
| 'MYSQL_PASSWORD' | Password of 'MYSQL_USER'. | MYSQL_PASSWORD="ChangeMe_keystone_db" |

### OpenStack Swift

| Variable | Description | Example |
|---|---|---|
| 'NB_MANAGEMENT_NODE' | Number of management nodes. One management node runs one proxy server. | NB_MANAGEMENT_NODE=1 |
| 'NB_STORAGE_NODE' | Number of storage nodes. One storage node runs one object, one container and one account server. It also sets the number of replicas in the rings. | NB_STORAGE_NODE=3 |
| 'NODE_STORAGE_SIZE' | Disk size of each storage node. Total space = 'NODE_STORAGE_SIZE' × 'NB_STORAGE_NODE'. On Kubernetes the value goes to 'fallocate': 10G = 10 GiB, 10GB = 10^9 bytes. | NODE_STORAGE_SIZE="10GB" |
| 'SWIFT_HASH_PREFIX' | Random secret used by Swift to place objects. **Never change it once the cluster holds data**, or the objects become unreachable. Generate it with 'openssl rand -hex 10'. | SWIFT_HASH_PREFIX="3f9a1c0b7e2d4a6f8c51" |
| 'SWIFT_HASH_SUFFIX' | Same as 'SWIFT_HASH_PREFIX'. | SWIFT_HASH_SUFFIX="a47e02d9c6b13f8e5d70" |
| 'SWIFT_PART_POWER' | Ring partition power (2^n partitions). Set when the ring is created. | SWIFT_PART_POWER=10 |
| 'SWIFT_MIN_PART_HOURS' | Minimum number of hours before a partition can move again after a rebalance. | SWIFT_MIN_PART_HOURS=1 |

### Keycloak / Keystone federation (OIDC)

| Variable | Description                                                                                                                                                                                                                  | Example |
|---|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---|
| 'FEDERATION_ENABLED' | OIDC federation between Keystone and Keycloak: true or false (password login only). Any value other than true means false. | FEDERATION_ENABLED="true" |
| 'DEPLOY_KEYCLOAK' | true: deploy the bundled Keycloak. false: use an external Keycloak, set in 'KEYCLOAK_URL'. Any value other than true means false. | DEPLOY_KEYCLOAK="true" |
| 'KEYCLOAK_URL' | Internal Keycloak URL, for server-to-server calls. No trailing slash, no '/realms' suffix. | KEYCLOAK_URL="http://keycloak:8080" |
| 'KEYCLOAK_PUBLIC_URL' | Public Keycloak URL, used for the SSO login redirect. Same as 'KEYCLOAK_URL' for an external Keycloak. | KEYCLOAK_PUBLIC_URL="http://localhost:8088" |
| 'KEYCLOAK_REALM' | Keycloak realm that holds the data lake users.                                                                                                                                                                               | KEYCLOAK_REALM="datalake" |
| 'KEYCLOAK_CLIENT_ID' | OIDC client declared in Keycloak for Keystone and Flask.                                                                                                                                                                     | KEYCLOAK_CLIENT_ID="keystone" |
| 'KEYCLOAK_CLIENT_SECRET' | Secret of that OIDC client.                                                                                                                                                                                                  | KEYCLOAK_CLIENT_SECRET="ChangeMe_client_secret" |
| 'KEYCLOAK_ISSUER' | Optional token issuer. Leave it empty to use '\${KEYCLOAK_PUBLIC_URL}/realms/\${KEYCLOAK_REALM}'. Only needed for an old Keycloak serving '/auth/realms/<realm>'. | KEYCLOAK_ISSUER="" |
| 'KEYCLOAK_ADMIN' | Admin username of the bundled Keycloak. Ignored when DEPLOY_KEYCLOAK="false".                                                                                                                                                | KEYCLOAK_ADMIN="admin" |
| 'KEYCLOAK_ADMIN_PASSWORD' | Admin password of the bundled Keycloak.                                                                                                                                                                                      | KEYCLOAK_ADMIN_PASSWORD="ChangeMe_keycloak_admin" |
| 'KEYCLOAK_HOST_PORT' | Host port of the bundled Keycloak, for browser and admin console access.                                                                                                                                                     | KEYCLOAK_HOST_PORT="8088" |
| 'OIDC_CRYPTO_PASSPHRASE' | Passphrase used by Apache 'mod_auth_openidc' to encrypt session cookies. Generate it with 'openssl rand -base64 32'. | OIDC_CRYPTO_PASSPHRASE="ChangeMe_long_random_oidc_passphrase" |
| 'KEYCLOAK_IDP_ID' | ID of the identity provider registered in Keystone.                                                                                                                                                                          | KEYCLOAK_IDP_ID="keycloak" |
| 'KEYCLOAK_PROTOCOL_ID' | Keystone federation protocol ID. Only mapped works for OIDC. | KEYCLOAK_PROTOCOL_ID="mapped" |
| 'KEYSTONE_PUBLIC_URL' | Public Keystone URL, used to build the OIDC redirect URI. No '/v3' suffix. | KEYSTONE_PUBLIC_URL="http://localhost:5000" |
| 'FEDERATED_DOMAIN' | Keystone domain for federated users and their projects, separate from 'Default'. On a running deployment, delete the identity provider before changing it. | FEDERATED_DOMAIN="keycloak" |
| 'FEDERATED_ROLE' | Role each federated user gets on their own project.                                                                                                                                                                          | FEDERATED_ROLE="bucket_owner" |
| 'FEDERATED_GROUP' | Keycloak group that gives access to the data lake. A user removed from it is refused at the next login, and their data is kept. | FEDERATED_GROUP="datalake_users" |
| 'FEDERATED_PROJECT' | Keystone project used by the federation mapping.                                                                                                                                                                             | FEDERATED_PROJECT="federated" |
| 'KEYCLOAK_SAMPLE_USER' | Sample user created in the bundled realm, for development.                                                                                                                                                                   | KEYCLOAK_SAMPLE_USER="datalake-user" |
| 'KEYCLOAK_SAMPLE_PASSWORD' | Password of the sample user.                                                                                                                                                                                                 | KEYCLOAK_SAMPLE_PASSWORD="ChangeMe_datalake_user" |

### Flask API

| Variable | Description | Example |
|---|---|---|
| 'KEYSTONE_URL' | Internal Keystone endpoint used by Flask, with the '/v3' suffix. | KEYSTONE_URL="http://keystone:5000/v3" |
| 'WEB_GUI_URL' | Public web GUI URL. Flask redirects the user there after an SSO login. | WEB_GUI_URL="http://localhost:7000" |
| 'FLASK_SECRET' | Key Flask uses to sign session cookies. Generate it with 'openssl rand -base64 32'. | FLASK_SECRET="ChangeMe_flask_session_secret" |
| 'IDP_READER_USER' | Read-only Keystone account used by Flask to list the identity providers (SSO buttons on the login page). | IDP_READER_USER="idp-reader" |
| 'IDP_READER_PASSWORD' | Password of 'IDP_READER_USER'. | IDP_READER_PASSWORD="ChangeMe_idp_reader" |

### Web GUI

| Variable | Description | Example |
|---|---|---|
| 'REACT_APP_FLASK_APP_URL' | Public Flask API URL, built into the React bundle. | REACT_APP_FLASK_APP_URL="http://localhost:7000/api" |
| 'REACT_APP_JUPYTERHUB_URL' | Public JupyterHub URL. | REACT_APP_JUPYTERHUB_URL="http://localhost:7000/hub" |
| 'REACT_APP_JUPYTERHUB_TOKEN' | JupyterHub API token used by the web GUI. | REACT_APP_JUPYTERHUB_TOKEN="ChangeMe_jupyterhub_token" |

### JupyterHub

| Variable | Description | Example |
|---|---|---|
| 'JUPYTERHUB_VERSION' | JupyterHub version used to build the hub image. | JUPYTERHUB_VERSION="5.3.0" |
| 'JUPYTERHUB_ADMIN' | Username with JupyterHub admin rights. | JUPYTERHUB_ADMIN="admin" |
| 'JUPYTERHUB_FLASK_URL' | Internal Flask URL used by the JupyterHub authenticator. | JUPYTERHUB_FLASK_URL="http://flask-app:5000" |
| 'JUPYTERHUB_PUBLIC_LOGIN_URL' | Public JupyterHub login URL. Flask redirects there after an SSO login. | JUPYTERHUB_PUBLIC_LOGIN_URL="http://localhost:7000/hub/hub/login" |
| 'DOCKER_NOTEBOOK_IMAGE' | Image JupyterHub starts for each user's notebook server. | DOCKER_NOTEBOOK_IMAGE="cors_base-notebook:latest" |

### Kubernetes platform only

**'k3s.yaml'** is the cluster's kubeconfig, at the repository root. If k3s runs on the same server, copy '/etc/rancher/k3s/k3s.yaml'. Otherwise, fill in 'k3s.yaml.example'. 'start.sh' sets 'KUBECONFIG' to this file for every script it runs.

The scripts of 'kubernetes/' are run from the repository root, like 'start.sh'. To run one by hand, set the kubeconfig first:

```bash
export KUBECONFIG="$PWD/k3s.yaml"
./kubernetes/kubernetes_config/disk_creation.sh --info
```

**'kubernetes/kubernetes_config/disks.env'** sets up the local disks of the Swift storage nodes. Copy it from 'disks.env.example'. The '--name' and '--size' options of 'disk_creation.sh' override 'DISK_NAME' and 'DISK_SIZE'.

| Variable | Description | Example |
|---|---|---|
| 'STORAGE_CLASS' | StorageClass whose discovery directory receives the disk (see 'local_static_provisioner.yml'). | STORAGE_CLASS="swift-disks" |
| 'DISK_NAME' | Default disk name. | DISK_NAME="d1" |
| 'DISK_SIZE' | Default disk size, in 'fallocate' syntax: '10G' = 10 GiB, '10GB' = 10^9 bytes. | DISK_SIZE="10G" |
| 'DISK_FS' | Filesystem of the Swift disks: xfs (recommended by Swift) or ext4. | DISK_FS="xfs" |
| 'IMG_DIR' | Folder of the disk image files. Must be on a local ext4 or XFS filesystem, outside 'DISKS_ROOT', not on a Windows drive ('/mnt/c', ...). | IMG_DIR="/var/lib/local-disks" |
| 'DISKS_ROOT' | Discovery root of the local static provisioner. Disks are mounted in 'DISKS_ROOT/STORAGE_CLASS/'. | DISKS_ROOT="/mnt/disks" |
| 'DISK_OWNER' | 'uid:gid' that owns the disk root. Empty means root. | DISK_OWNER="" |

## Usage

```bash
./start.sh --platform <docker-compose|kubernetes> [OPTIONS]
```

| Option | Action |
|---|---|
| '-b', '--build' | Build steps: configuration, initialization, images |
| '-r', '--run' | Start the data lake services |
| '-t', '--test' | Test mode: adds a Caddy reverse proxy |
| '-c', '--clean' | Remove stopped containers and orphans |
| '--clean-hard' | Full reset: deletes volumes, configuration and data |
| '--force-restart' | Restart every service, even unchanged ones. Kubernetes: 'kubectl rollout restart' of every Deployment and StatefulSet of the 'datalake' and 'datalake-jupyter' namespaces (the notebooks already started by the users keep running). Docker Compose: 'docker compose restart' of the 'datalake' and 'debug' profiles |
| '-h', '--help' | Show help |

'--platform' is mandatory. Examples:

```bash
./start.sh --platform docker-compose -brt   # build + run + test mode (recommended for development)
./start.sh --platform kubernetes -br        # build + run on k3s
```

## Kubernetes deployment

Install k3s and the Headlamp admin GUI:

```bash
./kubernetes/runK3S.sh install
./kubernetes/runK3S.sh gui
```

Then run 'start.sh' with '--platform kubernetes' (see [How does this repo work?](#how-does-this-repo-work)).

Migration status: Swift, memcached, the access zone, MariaDB and Keystone are migrated. Keycloak, Horizon and JupyterHub are still to be migrated.

WSL is for testing only, not for production.

### Access the services (Traefik)

Traefik, the Ingress controller bundled with k3s, is the only entry point of the cluster. It listens on 'KUBE_PUBLIC_PORT' (7000, like the docker-compose nginx) and sends every request to the 'nginx-proxy' Service, which routes by path ('/' to the web GUI, '/api/' to Flask, '/hub/' to JupyterHub).

JupyterHub is installed with the official Zero to JupyterHub chart, by k3s itself ('HelmChart' object generated by 'kubernetes/process_zone/jupyter/create_conf.sh', no helm tool needed), in the 'datalake-jupyter' namespace. It uses the Flask authenticator and login templates of 'process_zone/jupyter/'. Chart version, notebook image and sizes are set in the 'KUBERNETES CONF' section of 'conf.env'. Open http://localhost:7000/hub/. The other services ('nginx-proxy' included) are only reachable inside the cluster.

| File | Role |
|---|---|
| 'kubernetes/kubernetes_config/traefik_config.yml' | Port opened by Traefik on the machine ('KUBE_PUBLIC_PORT') |
| 'kubernetes/access_zone/ingress/ingress_datalake.yml' | Routing rule: every request to 'nginx-proxy' |

On the k3s machine, open http://localhost:7000 or http://<machine IP>:7000.

When the browser cannot reach the machine port directly (k3s on WSL: the port is opened on the WSL IP, not on Windows 'localhost'; or a VPN that blocks local network traffic), forward the Traefik port. From the repository root:

```bash
export KUBECONFIG="$PWD/k3s.yaml"
kubectl -n kube-system port-forward svc/traefik 7000:7000
```

Keep the command running, then open http://localhost:7000 in the browser. It stops when the terminal is closed or the Traefik pod restarts: run it again.

With the bundled Keycloak ('DEPLOY_KEYCLOAK="true"'), the browser must also reach Keycloak at 'KEYCLOAK_PUBLIC_URL' (SSO login page, admin console). Forward 'KEYCLOAK_HOST_PORT' the same way, in a second terminal:

```bash
kubectl -n datalake port-forward svc/keycloak-public 8088:8088
```

Keycloak is not behind Traefik yet: it still has its own port ('KEYCLOAK_HOST_PORT').

### Change a value of conf.env (Kubernetes)

Run '-br' again. '-r' only restarts the services whose generated configuration changed: each pod carries a checksum of its configuration (annotation 'checksum/config'), and Kubernetes replaces the pods when it changes. Services call each other by Service name ('keystone:5000', 'swift-proxy:8080', 'mariadb:3306', 'keycloak:8080'), so a restarted pod is found again without any change. From another namespace (JupyterHub in 'datalake-jupyter'), the full name is used: 'flask-app.datalake.svc.cluster.local:5000', and the Swift endpoints of the Keystone catalog are 'http://swift-proxy.datalake.svc.cluster.local:8080/...' so that the notebooks can use them too.

Use '--force-restart' when an image was rebuilt with the same tag ('swift-base', 'keystone', 'mariadb', or the Flask and web GUI images without a new git commit): the configuration did not change, so '-r' restarts nothing.

```bash
./start.sh --platform kubernetes --force-restart
```

Some values are only read when a service is initialized, the first time. Changing them in 'conf.env' is not enough:

| Value | Why | What to do |
|---|---|---|
| 'MYSQL_*' | MariaDB creates root, the database and its user on an empty disk only. A new 'MYSQL_PASSWORD' goes to 'keystone.conf' but not to the database ("Access denied"). | Change it in MariaDB too ('ALTER USER'), then '-br'. |
| 'KEYCLOAK_ADMIN_PASSWORD' | Keycloak creates its admin at the first start only. | Change it in the Keycloak admin console. |
| Keycloak realm ('KEYCLOAK_CLIENT_SECRET', 'KEYCLOAK_SAMPLE_*', 'WEB_GUI_URL' in the redirect URIs) | The realm is imported only when it does not exist, to keep the users. | Change the client in the Keycloak admin console. A wrong client secret breaks the SSO login. |
| 'REACT_APP_*' | Built into the web GUI image. | '-b', then '--force-restart' if the git commit did not change. |
| 'SWIFT_HASH_PREFIX', 'SWIFT_HASH_SUFFIX' | Part of the path of every stored object. | Never change them once Swift holds data. |

'OS_PASSWORD' and the Swift endpoints of the Keystone catalog are applied again at every deployment.

## Troubleshooting

### Docker Compose: Swift storage raises "no space left"

The storage setup only uses '/dev/loop0'. If that loop device is already in use, release it:

```bash
sudo losetup -d /dev/loop0
```

### Kubernetes: local static provisioner stuck in 'CreateContainerError'

If the 'local-static-provisioner' pod stays in 'CreateContainerError' with a message such as:

```
path "/mnt/disks" is mounted on "/mnt/d" but it is not a shared or slave mount
```

'/mnt/d' (the Windows 'D:' drive on WSL) is a prefix of '/mnt/disks', and containerd takes it as the parent mount of '/mnt/disks'. Make '/mnt/disks' its own shared mount, then recreate the pod:

```bash
sudo mount --rbind /mnt/disks /mnt/disks
sudo mount --make-rshared /mnt/disks
kubectl -n kube-system delete pod -l app.kubernetes.io/name=local-static-provisioner
```

To run again after each reboot.

## Testing

OpenStack CLI environment:

```bash
export OS_USERNAME=admin
export OS_PASSWORD=<admin password from conf.env>
export OS_PROJECT_NAME=admin
export OS_USER_DOMAIN_NAME=Default
export OS_PROJECT_DOMAIN_NAME=Default
export OS_AUTH_URL=http://localhost:5000/v3
export OS_IDENTITY_API_VERSION=3
export OS_IMAGE_API_VERSION=2
```

Flask API (Docker Compose), with a Keystone token or with credentials:

```bash
export OS_TOKEN=$(openstack token issue -f value -c id)
curl -H "Authorization: Bearer $OS_TOKEN" http://localhost:3001/buckets
curl -H "X-Username: $OS_USERNAME" -H "X-Password: $OS_PASSWORD" \
     -H "Content-Type: application/json" http://localhost:3001/buckets
```

## Roadmap

- [ ] Distributed architecture
  - [ ] Swift multi-node
  - [ ] Scripts management
- [ ] Kubernetes migration (in progress)
- [ ] Test scripts
- [ ] Keystone bootstrap: create an endpoint for each management node
- [ ] Test bucket listing with a token provided in the request
- [ ] Docker Compose: use the loop device actually created instead of always '/dev/loop0'
- [ ] JupyterHub: replace SQLite with a client-server database (MariaDB)
  - [ ] Reuse Keystone's MariaDB
  - [ ] High-availability MariaDB
  - [ ] Multi-server deployment

### Security

- [ ] Docker Compose: Swift containers run in privileged mode, give them an explicit list of capabilities instead (already done in the Kubernetes manifests).

### Deferred: centralize Keystone token management in Flask

The web GUI stores the Keystone token in 'localStorage' and local credentials in 'sessionStorage'. Moving token management to Flask would allow opening Keystone to external identity providers without exposing tokens in the browser. Not a priority for now.

Target: Flask manages authentication and sessions for every client.

- Keystone tokens are stored in Valkey, the browser only gets an 'HttpOnly' session cookie.
- Local login and federated SSO share the same server-side session.
- Keystone tokens and passwords are removed from browser storage and from API responses.
- Every API request authenticates through the Flask session.
- Logout revokes the Keystone token and deletes the session.
- JupyterHub authenticates through short-lived tickets issued by Flask.

## License

This project is licensed under the GNU Affero General Public License v3.0. See [LICENSE](LICENSE).

Copyright (C) 2020-2026 Vincent-Nam DANG
Copyright (C) 2021-2026 docker_datalake contributors

The software license does not apply to data, notebooks, business scripts, queries, models, results, configurations, or other independent content merely because they are used by, provided to, or created with the project. These items remain subject to the rights and licenses chosen by their respective owners.

Third-party components used or executed by the project, particularly in the form of separate containers, remain governed by their respective licenses.
