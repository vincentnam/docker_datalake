#!/bin/bash


export $(grep -v '^#' ./conf.env | sed 's/\r$//' | xargs)
OPENSTACKKEYSTONE_PATH="./rawdata_zone/openstackKeystone"
OPENSTACKKEYSTONE_KUBE_PATH="./kubernetes/rawdata_zone/openstackKeystone"

if [ -z "$MYSQL_ROOT_PASSWORD" ]; then
  echo "Set the MariaDB root password in conf.env file."
  exit 1
fi

if [ -z "$MYSQL_DATABASE" ]; then
  echo "Set the Keystone database name in conf.env file."
  exit 1
fi

if [ -z "$MYSQL_USER" ]; then
  echo "Set the Keystone database user in conf.env file."
  exit 1
fi

if [ -z "$MYSQL_PASSWORD" ]; then
  echo "Set the Keystone database password in conf.env file."
  exit 1
fi

if [ -z "$OS_PASSWORD" ]; then
  echo "Set the Admin account password in conf.env file."
  exit 1
fi

if [ -z "$SWIFT_PASSWORD" ]; then
  echo "Set the Swift account password in conf.env file."
  exit 1
fi

if [ -z "$OIDC_CRYPTO_PASSPHRASE" ]; then
  echo "Set the OIDC crypto passphrase in conf.env file."
  exit 1
fi

if [ -z "$KEYCLOAK_PUBLIC_URL" ]; then
  echo "Set the Keycloak public URL in conf.env file."
  exit 1
fi

if [ -z "$KEYCLOAK_REALM" ]; then
  echo "Set the Keycloak realm in conf.env file."
  exit 1
fi

# Same values as create_docker.sh
KEYCLOAK_ISSUER="${KEYCLOAK_ISSUER:-${KEYCLOAK_PUBLIC_URL%/}/realms/$KEYCLOAK_REALM}"
KEYCLOAK_JWKS_URI="${KEYCLOAK_URL%/}/realms/$KEYCLOAK_REALM/protocol/openid-connect/certs"

# The database password goes into a URL (connection line of keystone.conf) : its special characters are
# URL-encoded. This also keeps & and # out of the sed replacement below.
MYSQL_PASSWORD_URL=$(printf '%s' "$MYSQL_PASSWORD" | sed -e 's/%/%25/g' -e 's/ /%20/g' -e 's/!/%21/g' -e 's/#/%23/g' -e 's/\$/%24/g' -e 's/&/%26/g' -e "s/'/%27/g" -e 's#/#%2F#g' -e 's/:/%3A/g' -e 's/?/%3F/g' -e 's/@/%40/g' -e 's/\\/%5C/g')

# Full Service name of the Swift proxy in the Keystone catalog : the short name only resolves in the datalake
# namespace, the notebooks (datalake-jupyter) and the future tenants read the same catalog.
SWIFT_PROXY_URL="http://swift-proxy.datalake.svc.cluster.local:8080"

mkdir -p $OPENSTACKKEYSTONE_KUBE_PATH/volumes


###################################
# MARIADB
###################################
# Read by the MariaDB image at the first start only (empty disk) : creates root, the database and its user.
# Values are written between double quotes : a " or a \ in a value of conf.env breaks the file.
cat << EOF > $OPENSTACKKEYSTONE_KUBE_PATH/volumes/secret_mariadb_env.yml
apiVersion: v1
kind: Secret
metadata:
  name: mariadb-env
  namespace: datalake
  labels:
    app.kubernetes.io/name: mariadb
    app.kubernetes.io/part-of: security-zone
type: Opaque
stringData:
  MARIADB_ROOT_PASSWORD: "$MYSQL_ROOT_PASSWORD"
  MARIADB_DATABASE: "$MYSQL_DATABASE"
  MARIADB_USER: "$MYSQL_USER"
  MARIADB_PASSWORD: "$MYSQL_PASSWORD"
EOF
chmod 600 $OPENSTACKKEYSTONE_KUBE_PATH/volumes/secret_mariadb_env.yml


###################################
# KEYSTONE CONF FILES
###################################
# The files of the Compose service folder, mounted at the same paths as in docker-compose.
# keystone.conf is a Secret : it holds the database password (connection line rewritten like the root create_conf.sh).
cat << EOF > $OPENSTACKKEYSTONE_KUBE_PATH/volumes/secret_keystone_conf.yml
apiVersion: v1
kind: Secret
metadata:
  name: keystone-conf
  namespace: datalake
  labels:
    app.kubernetes.io/name: keystone
    app.kubernetes.io/part-of: security-zone
type: Opaque
stringData:
  keystone.conf: |
$(sed -e 's/\r$//' -e "s#^connection = .*#connection = mysql+pymysql://${MYSQL_USER}:${MYSQL_PASSWORD_URL}@mariadb/${MYSQL_DATABASE}#" -e 's/^/    /' $OPENSTACKKEYSTONE_PATH/conf/etc/keystone/keystone.conf)
EOF
chmod 600 $OPENSTACKKEYSTONE_KUBE_PATH/volumes/secret_keystone_conf.yml

# The Swift endpoints of bootstrap_keystone.sh point to the Compose proxy (management-1) : full Service name of swift-proxy here.
cat << EOF > $OPENSTACKKEYSTONE_KUBE_PATH/volumes/configmap_keystone_files.yml
apiVersion: v1
kind: ConfigMap
metadata:
  name: keystone-files
  namespace: datalake
  labels:
    app.kubernetes.io/name: keystone
    app.kubernetes.io/part-of: security-zone
data:
  policy.yaml: |
$(sed -e 's/\r$//' -e 's/^/    /' $OPENSTACKKEYSTONE_PATH/conf/etc/keystone/policy.yaml)
  ports.conf: |
$(sed -e 's/\r$//' -e 's/^/    /' $OPENSTACKKEYSTONE_PATH/conf/apache2/keystone/ports.conf)
  keystone-site.conf: |
$(sed -e 's/\r$//' -e 's/^/    /' $OPENSTACKKEYSTONE_PATH/conf/apache2/keystone/sites-available/keystone.conf)
  wsgi.py: |
$(sed -e 's/\r$//' -e 's/^/    /' $OPENSTACKKEYSTONE_PATH/conf/python/keystone/wsgi/wsgi.py)
  init-keystone.sh: |
$(sed -e 's/\r$//' -e 's/^/    /' $OPENSTACKKEYSTONE_PATH/scripts/init-keystone.sh)
  bootstrap_keystone.sh: |
$(sed -e 's/\r$//' -e "s#http://management-1:8080#$SWIFT_PROXY_URL#g" -e 's/^/    /' $OPENSTACKKEYSTONE_PATH/scripts/bootstrap_keystone.sh)
EOF


###################################
# KEYSTONE ENVIRONMENT
###################################
# Same variables as the keystone and keystone_bootstrap services of create_docker.sh.
# Both pods read the ConfigMap and the Secret : each script uses its own variables.
cat << EOF > $OPENSTACKKEYSTONE_KUBE_PATH/volumes/configmap_keystone_env.yml
apiVersion: v1
kind: ConfigMap
metadata:
  name: keystone-env
  namespace: datalake
  labels:
    app.kubernetes.io/name: keystone
    app.kubernetes.io/part-of: security-zone
data:
  OS_AUTH_URL: "http://keystone:5000/v3"
  OS_USERNAME: "$OS_USERNAME"
  OS_PROJECT_NAME: "admin"
  OS_USER_DOMAIN_NAME: "Default"
  OS_PROJECT_DOMAIN_NAME: "Default"
  FEDERATION_ENABLED: "$FEDERATION_ENABLED"
  KEYCLOAK_ISSUER: "$KEYCLOAK_ISSUER"
  KEYCLOAK_JWKS_URI: "$KEYCLOAK_JWKS_URI"
  KEYCLOAK_CLIENT_ID: "$KEYCLOAK_CLIENT_ID"
  KEYCLOAK_IDP_ID: "$KEYCLOAK_IDP_ID"
  KEYCLOAK_PROTOCOL_ID: "$KEYCLOAK_PROTOCOL_ID"
  KEYSTONE_PUBLIC_URL: "$KEYSTONE_PUBLIC_URL"
  FEDERATED_DOMAIN: "$FEDERATED_DOMAIN"
  FEDERATED_GROUP: "$FEDERATED_GROUP"
  FEDERATED_PROJECT: "$FEDERATED_PROJECT"
  FEDERATED_ROLE: "$FEDERATED_ROLE"
  IDP_READER_USER: "$IDP_READER_USER"
EOF

cat << EOF > $OPENSTACKKEYSTONE_KUBE_PATH/volumes/secret_keystone_env.yml
apiVersion: v1
kind: Secret
metadata:
  name: keystone-env
  namespace: datalake
  labels:
    app.kubernetes.io/name: keystone
    app.kubernetes.io/part-of: security-zone
type: Opaque
stringData:
  OS_PASSWORD: "$OS_PASSWORD"
  SWIFT_PASSWORD: "$SWIFT_PASSWORD"
  KEYCLOAK_CLIENT_SECRET: "$KEYCLOAK_CLIENT_SECRET"
  OIDC_CRYPTO_PASSPHRASE: "$OIDC_CRYPTO_PASSPHRASE"
  IDP_READER_PASSWORD: "$IDP_READER_PASSWORD"
EOF
chmod 600 $OPENSTACKKEYSTONE_KUBE_PATH/volumes/secret_keystone_env.yml


###################################
# KEYSTONE KEYS (fernet + credential)
###################################
# Created ONCE, straight in the cluster (never written on disk, never in git) :
#  - new fernet keys invalidate every token
#  - new credential keys make the credentials of an existing database unreadable
# Rotation : Airflow routine (kanban AirflowRoutine). Key = 32 random bytes, URL-safe base64.
# 0 = staged key, 1 = primary key (same layout as keystone-manage fernet_setup).
kubectl apply --server-side -f ./kubernetes/namespace_datalake.yml

if kubectl -n datalake get secret keystone-fernet-keys >/dev/null 2>&1; then
  echo "Secret keystone-fernet-keys already in the cluster : keys kept."
else
  kubectl -n datalake create secret generic keystone-fernet-keys \
    --from-literal=0="$(head -c 32 /dev/urandom | base64 | tr '+/' '-_')" \
    --from-literal=1="$(head -c 32 /dev/urandom | base64 | tr '+/' '-_')"
  kubectl -n datalake label secret keystone-fernet-keys app.kubernetes.io/name=keystone app.kubernetes.io/part-of=security-zone
fi

if kubectl -n datalake get secret keystone-credential-keys >/dev/null 2>&1; then
  echo "Secret keystone-credential-keys already in the cluster : keys kept."
else
  kubectl -n datalake create secret generic keystone-credential-keys \
    --from-literal=0="$(head -c 32 /dev/urandom | base64 | tr '+/' '-_')" \
    --from-literal=1="$(head -c 32 /dev/urandom | base64 | tr '+/' '-_')"
  kubectl -n datalake label secret keystone-credential-keys app.kubernetes.io/name=keystone app.kubernetes.io/part-of=security-zone
fi
