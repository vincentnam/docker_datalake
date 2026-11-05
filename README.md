# docker_datalake

A self-hosted data lake built on OpenStack components, automatically deployable with Docker Compose or Kubernetes (k3s).

## Architecture

| Zone             | Services                                                                                                                                                       | Role                                                                |
|------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------|
| Raw data zone    | Included : OpenStack Swift (proxy + storage nodes),                                                                                                            | Store raw data with no modification at the lowest cost possible     |
| Access zone      | Included : Flask REST API (single entry point), React web GUI (User friendly interaction)                                                                      | Allow interaction with differents data lake services                |
| Process zone     | Included : JupyterHub / Planned : Airflow (for orchestration) - Apache Spark + Apache Spark Streaming (for data stream)                                        | "Brain" part : orchestration + data exploration + stream management |
| Consumption zone | Planned : Kubernetes / Docker (not managed)                                                                                                                    | Deploy multiple services to consume data                            |
| Security Zone    | Included : Openstack Keystone + MariaDB (local IDP + federated IDP for Swift (mandatory)) + external IDP (Keycloak as default), nginx reverse proxy (security) | Manage authentication                                               |
| Govern Zone      | Planned : MongoDB ( metadata management )                                                                                                                      | Data lifecycle management                                           |
| Other            | Memcached ( data lake caching system )                                                                                                                         |                                                                     |

## Requirements

Docker :
- Linux host
- Docker
- 'sudo' (at the moment, no test version with root account)
- 'getopt' 
Kubernetes platform (K3S platform) :
- kubectl
- envsubst
- systemd
WSL (Test and dev only purpose)
- "[boot] systemd=true" in /etc/wsl.conf
- run these commands if a folder starts with the letter "d" 

  sudo mount --rbind /mnt/disks /mnt/disks
  sudo mount --make-rshared /mnt/disks

## How does this repo work?

Each service has its own folder, grouped by zone. For example, OpenStack Swift lives in 'rawdata_zone/openstackSwift/'. Every service runs in containers, deployed with Docker Compose or Kubernetes. All settings (passwords, replicas, storage size, ports, etc.) come from a single file, 'conf.env'.

'start.sh' is the single entry point for both platforms:

- **Build ('-b')** turns 'conf.env' into the configuration files of each service and builds the images.
- **Run ('-r')** starts the services.

### Docker Compose

1. 'create_conf.sh' writes each service's configuration files into its folder.
2. 'create_docker.sh' generates 'docker-compose_datalake.yml' from that configuration.
3. 'start.sh' builds the Keystone and JupyterHub images and initializes Swift.
4. With '-r', 'docker compose up' starts every service. Test mode ('-t') adds a Caddy reverse proxy. (Planned to be removed)

### Kubernetes (k3s)

Kubernetes manifests live in 'kubernetes/', with the same zone layout as the Docker Compose files.

1. 'disk_creation.sh' creates one local XFS disk per Swift storage node and exposes it to the cluster as a PersistentVolume.
2. 'start.sh' builds the Swift, Flask and web GUI images, then imports them into k3s's containerd. The build must therefore run on a k3s node.
3. Each service's 'create_conf.sh' generates its configuration (ConfigMaps and Secrets) from 'conf.env', and 'create_rings.sh' builds the Swift rings.
4. With '-r', 'deploy.sh' fills the variables of the manifests (image tag, replicas, storage size) with 'envsubst' and applies them with 'kubectl apply'.


## Configuration

All settings live in 'conf.env', at the repository root. Each line of the file has the form NAME="value". The Example column shows the complete line to write in 'conf.env'.

> Change every 'ChangeMe' value and every password before deploying. Never commit a 'conf.env' that holds real secrets.

### OpenStack Keystone build (LOCI)

| Variable | Description | Example |
|---|---|---|
| 'OPENSTACK_RELEASE_VAR' | OpenStack release used to build Keystone and Horizon: the branch name of their repositories (see [releases.openstack.org](https://releases.openstack.org/)). | OPENSTACK_RELEASE_VAR="stable/2026.1" |
| 'BASE_DISTRO_VAR' | Base OS image of the Keystone build. | BASE_DISTRO_VAR="ubuntu:noble" |
| 'BASE_TAG_VAR' | Tag of the built Keystone image. Free to change. | BASE_TAG_VAR="ubuntu_noble" |
| 'OS_USERNAME' | Username of the Keystone admin account, used for bootstrap and admin operations. | OS_USERNAME="admin" |
| 'OS_PASSWORD' | Password of the Keystone admin account. **Required**; 12 characters or more recommended. | OS_PASSWORD="ChangeMe_admin_password" |
| 'SWIFT_PASSWORD' | Password of the 'swift' service account in Keystone. **Required**; 12 characters or more recommended. | SWIFT_PASSWORD="ChangeMe_swift_password" |

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
| 'NODE_STORAGE_SIZE' | Disk size of each storage node. Total space = 'NODE_STORAGE_SIZE' × 'NB_STORAGE_NODE'. | NODE_STORAGE_SIZE="10GB" |
| 'SWIFT_HASH_PREFIX' | Random secret string that Swift uses to compute where each object is stored. **Never change it once the cluster holds data**: existing objects would become unreachable. Generate it with 'openssl rand -hex 10'. | SWIFT_HASH_PREFIX="3f9a1c0b7e2d4a6f8c51" |
| 'SWIFT_HASH_SUFFIX' | Same role and same rule as 'SWIFT_HASH_PREFIX'. Generate it with 'openssl rand -hex 10'. | SWIFT_HASH_SUFFIX="a47e02d9c6b13f8e5d70" |
| 'SWIFT_PART_POWER' | Ring partition power: the ring has 2^n partitions. Fixed when the ring is created. | SWIFT_PART_POWER=10 |
| 'SWIFT_MIN_PART_HOURS' | Minimum number of hours before a partition can move again after a rebalance. | SWIFT_MIN_PART_HOURS=1 |

### Keycloak / Keystone federation (OIDC)

| Variable | Description                                                                                                                                                                                                                  | Example |
|---|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---|
| 'FEDERATION_ENABLED' | Turns on OIDC federation between Keystone and Keycloak. Values: true (federation on) or false (Keystone uses passwords only). Case-insensitive; any value other than 'true' counts as 'false'.                               | FEDERATION_ENABLED="true" |
| 'DEPLOY_KEYCLOAK' | Chooses which Keycloak to use. Values: true (deploy the bundled Keycloak) or false (reuse an external Keycloak, set in 'KEYCLOAK_URL'). Case-insensitive; any value other than 'true' counts as 'false'.                     | DEPLOY_KEYCLOAK="true" |
| 'KEYCLOAK_URL' | Internal Keycloak base URL, for server-to-server calls. No trailing slash and no '/realms' suffix.                                                                                                                           | KEYCLOAK_URL="http://keycloak:8080" |
| 'KEYCLOAK_PUBLIC_URL' | Keycloak base URL as the browser reaches it, for the SSO login redirect. For an external Keycloak, use the same value as 'KEYCLOAK_URL'.                                                                                     | KEYCLOAK_PUBLIC_URL="http://localhost:8088" |
| 'KEYCLOAK_REALM' | Keycloak realm that holds the data lake users.                                                                                                                                                                               | KEYCLOAK_REALM="datalake" |
| 'KEYCLOAK_CLIENT_ID' | OIDC client declared in Keycloak for Keystone and Flask.                                                                                                                                                                     | KEYCLOAK_CLIENT_ID="keystone" |
| 'KEYCLOAK_CLIENT_SECRET' | Secret of that OIDC client.                                                                                                                                                                                                  | KEYCLOAK_CLIENT_SECRET="ChangeMe_client_secret" |
| 'KEYCLOAK_ISSUER' | Optional override of the token issuer. Leave it empty to use '\${KEYCLOAK_PUBLIC_URL}/realms/\${KEYCLOAK_REALM}'. Set it only for a legacy Keycloak that serves '/auth/realms/<realm>'.                                      | KEYCLOAK_ISSUER="" |
| 'KEYCLOAK_ADMIN' | Admin username of the bundled Keycloak. Ignored when DEPLOY_KEYCLOAK="false".                                                                                                                                                | KEYCLOAK_ADMIN="admin" |
| 'KEYCLOAK_ADMIN_PASSWORD' | Admin password of the bundled Keycloak.                                                                                                                                                                                      | KEYCLOAK_ADMIN_PASSWORD="ChangeMe_keycloak_admin" |
| 'KEYCLOAK_HOST_PORT' | Host port of the bundled Keycloak, for browser and admin console access.                                                                                                                                                     | KEYCLOAK_HOST_PORT="8088" |
| 'OIDC_CRYPTO_PASSPHRASE' | Passphrase that Apache 'mod_auth_openidc' uses to encrypt session cookies. Long, random and secret: generate it with 'openssl rand -base64 32'.                                                                              | OIDC_CRYPTO_PASSPHRASE="ChangeMe_long_random_oidc_passphrase" |
| 'KEYCLOAK_IDP_ID' | ID of the identity provider registered in Keystone.                                                                                                                                                                          | KEYCLOAK_IDP_ID="keycloak" |
| 'KEYCLOAK_PROTOCOL_ID' | Keystone federation protocol ID. Value: mapped, the only value valid for OIDC (Keystone 2026.1 has no 'openid' auth method).                                                                                                 | KEYCLOAK_PROTOCOL_ID="mapped" |
| 'KEYSTONE_PUBLIC_URL' | Keystone URL as the browser reaches it, used to build the OIDC redirect URI. No '/v3' suffix.                                                                                                                                | KEYSTONE_PUBLIC_URL="http://localhost:5000" |
| 'FEDERATED_DOMAIN' | Keystone domain for federated users and their projects. It is kept apart from 'Default' so that Keycloak usernames never collide with local accounts. To change it on a live deployment, delete the identity provider first. | FEDERATED_DOMAIN="keycloak" |
| 'FEDERATED_ROLE' | Role each federated user gets on their own project.                                                                                                                                                                          | FEDERATED_ROLE="bucket_owner" |
| 'FEDERATED_GROUP' | Keycloak group that grants data lake access. A user removed from the group is refused at their next login; their data is kept.                                                                                               | FEDERATED_GROUP="datalake_users" |
| 'FEDERATED_PROJECT' | Keystone project used by the federation mapping.                                                                                                                                                                             | FEDERATED_PROJECT="federated" |
| 'KEYCLOAK_SAMPLE_USER' | Sample user created in the bundled realm, for development.                                                                                                                                                                   | KEYCLOAK_SAMPLE_USER="datalake-user" |
| 'KEYCLOAK_SAMPLE_PASSWORD' | Password of the sample user.                                                                                                                                                                                                 | KEYCLOAK_SAMPLE_PASSWORD="ChangeMe_datalake_user" |

### Flask API

| Variable | Description | Example |
|---|---|---|
| 'KEYSTONE_URL' | Internal Keystone endpoint used by Flask, with the '/v3' suffix. | KEYSTONE_URL="http://keystone:5000/v3" |
| 'WEB_GUI_URL' | Public web GUI URL. Flask redirects the user there after an SSO login. | WEB_GUI_URL="http://localhost:7000" |
| 'FLASK_SECRET' | Key Flask uses to sign session cookies. Generate it with 'openssl rand -base64 32'. | FLASK_SECRET="ChangeMe_flask_session_secret" |
| 'IDP_READER_USER' | Read-only Keystone service account. Flask uses it to list identity providers, which drive the SSO buttons on the login page. | IDP_READER_USER="idp-reader" |
| 'IDP_READER_PASSWORD' | Password of 'IDP_READER_USER'. | IDP_READER_PASSWORD="ChangeMe_idp_reader" |

### Web GUI

| Variable | Description | Example |
|---|---|---|
| 'REACT_APP_FLASK_APP_URL' | Flask API URL as the browser reaches it. It is built into the React bundle. | REACT_APP_FLASK_APP_URL="http://localhost:7000/api" |
| 'REACT_APP_JUPYTERHUB_URL' | JupyterHub URL as the browser reaches it. | REACT_APP_JUPYTERHUB_URL="http://localhost:7000/hub" |
| 'REACT_APP_JUPYTERHUB_TOKEN' | JupyterHub API token used by the web GUI. | REACT_APP_JUPYTERHUB_TOKEN="ChangeMe_jupyterhub_token" |

### JupyterHub

| Variable | Description | Example |
|---|---|---|
| 'JUPYTERHUB_VERSION' | JupyterHub version used to build the hub image. | JUPYTERHUB_VERSION="5.3.0" |
| 'JUPYTERHUB_ADMIN' | Username with JupyterHub admin rights. | JUPYTERHUB_ADMIN="admin" |
| 'JUPYTERHUB_FLASK_URL' | Internal Flask URL used by the JupyterHub authenticator. | JUPYTERHUB_FLASK_URL="http://flask-app:5000" |
| 'JUPYTERHUB_PUBLIC_LOGIN_URL' | JupyterHub login URL as the browser reaches it. Flask redirects there after an SSO login. | JUPYTERHUB_PUBLIC_LOGIN_URL="http://localhost:7000/hub/hub/login" |
| 'DOCKER_NOTEBOOK_IMAGE' | Image JupyterHub starts for each user's notebook server. | DOCKER_NOTEBOOK_IMAGE="cors_base-notebook:latest" |

### Kubernetes platform only

**'k3s.yaml'** is the cluster's kubeconfig, at the repository root. If k3s runs on the same server, copy '/etc/rancher/k3s/k3s.yaml'. Otherwise, fill in 'k3s.yaml.example'.

**'kubernetes/kubernetes_config/disks.env'** sets up the local disks of the Swift storage nodes. Copy it from 'disks.env.example'. The '--name' and '--size' options of 'disk_creation.sh' override 'DISK_NAME' and 'DISK_SIZE'. In the table below, the Example column shows the complete line to write in 'disks.env'.

| Variable | Description | Example |
|---|---|---|
| 'STORAGE_CLASS' | StorageClass whose discovery directory receives the disk (see 'local_static_provisioner.yml'). | STORAGE_CLASS="swift-disks" |
| 'DISK_NAME' | Default disk name. | DISK_NAME="d1" |
| 'DISK_SIZE' | Default disk size, in 'fallocate' syntax: '10G' = 10 GiB, '10GB' = 10^9 bytes. | DISK_SIZE="10G" |
| 'DISK_FS' | Filesystem of the Swift disks. Values: 'xfs' (recommended by Swift) or 'ext4' (extended attributes limited to about 4 KB per file). Any other value stops 'disk_creation.sh' with an error. | DISK_FS="xfs" |
| 'IMG_DIR' | Folder that holds the disk image files. It must be on a local ext4 or XFS filesystem, outside 'DISKS_ROOT', and not on a Windows drive ('/mnt/c', ...). | IMG_DIR="/var/lib/local-disks" |
| 'DISKS_ROOT' | Discovery root of the local static provisioner. Disks are mounted in 'DISKS_ROOT/STORAGE_CLASS/'. | DISKS_ROOT="/mnt/disks" |
| 'KUBECONFIG_FILE' | kubeconfig used by '--apply'. | KUBECONFIG_FILE="/etc/rancher/k3s/k3s.yaml" |
| 'DISK_OWNER' | 'uid:gid' that owns the disk root. Empty means root. | DISK_OWNER="" |

## Usage

```bash
./start.sh --platform <docker-compose|kubernetes> [OPTIONS]
```

| Option | Action |
|---|---|
| '-b', '--build' | Build steps: configuration, initialisation, images |
| '-r', '--run' | Start the data lake services |
| '-t', '--test' | Test mode: adds a Caddy reverse proxy |
| '-c', '--clean' | Remove stopped containers and orphans |
| '--clean-hard' | Full reset: deletes volumes, configuration and data |
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

With '--platform kubernetes':

- '-b' creates the local Swift disks, builds the images and imports them into k3s, then generates the Swift configuration, the Swift rings and the access zone configuration.
- '-r' applies the manifests through 'kubernetes/deploy.sh'.

Migration status: Swift, memcached and the access zone are migrated. MariaDB, Keystone, Keycloak, Horizon and JupyterHub are still to be migrated.

> WSL is supported for testing only. Do not deploy this architecture on WSL in production.

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

the cause is a disk mount issue: another mount point's path is a string prefix of '/mnt/disks'. The usual culprit is the Windows 'D:' drive, which WSL mounts at '/mnt/d'. containerd matches mount points by string prefix rather than by path. It therefore takes '/mnt/d' (private propagation) as the parent mount of '/mnt/disks', and rejects the 'HostToContainer' mount propagation the provisioner requires.

To fix it, make '/mnt/disks' its own shared mount, then recreate the pod:

```bash
sudo mount --rbind /mnt/disks /mnt/disks
sudo mount --make-rshared /mnt/disks
kubectl -n kube-system delete pod -l app.kubernetes.io/name=local-static-provisioner
```

These commands do not persist across reboots.

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
- [ ] Kubernetes migration (in progress, see the migration guide)
- [ ] Test scripts
- [ ] Keystone bootstrap: create an endpoint for each management node
- [ ] Test bucket listing with a token provided in the request
- [ ] Docker Compose: use the loop device actually created instead of always '/dev/loop0'
- [ ] JupyterHub: replace SQLite with an SQL database
  - [ ] Reuse Keystone's MariaDB
  - [ ] High-availability MariaDB
  - [ ] Multi-server deployment

### Security

- [ ] Docker Compose: Swift containers run in privileged mode. Grant an explicit list of capabilities instead. (The Kubernetes manifests already run Swift unprivileged.)

### Deferred: centralize Keystone token management in Flask

**Current situation.** The web GUI stores the Keystone token in 'localStorage' and local credentials in 'sessionStorage'. Flask is already the only public gateway, so this change is useful but not a priority. It would allow the Keystone service to be opened (for authentication federation from external identity providers to the internal Keystone) without exposing Keystone tokens through the web GUI.

**Target architecture.** Flask becomes the single authentication and session authority for every data lake client:

- Keystone tokens are stored in Valkey; the browser only receives an 'HttpOnly' session cookie.
- Local login and federated SSO share the same server-side session.
- Keystone tokens and passwords are removed from browser storage and from API responses.
- Every API request authenticates through the Flask session.
- Logout revokes the Keystone token and deletes the session.
- JupyterHub authenticates through short-lived tickets issued by Flask.

## Licence

This project is licensed under the GNU Affero General Public License v3.0. See [LICENSE](LICENSE).

Copyright (C) 2020-2026 Vincent-Nam DANG
Copyright (C) 2021-2026 docker_datalake contributors

The software licence does not apply to data, notebooks, business scripts, queries, models, results, configurations, or other independent content merely because they are used by, provided to, or created with the project. These items remain subject to the rights and licences chosen by their respective owners.

Third-party components used or executed by the project, particularly in the form of separate containers, remain governed by their respective licences.
