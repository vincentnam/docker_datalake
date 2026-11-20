#!/bin/bash


export $(grep -v '^#' ./conf.env | sed 's/\r$//' | xargs)
ACCESS_ZONE_KUBE_PATH="./kubernetes/access_zone"

if [ -z "$FLASK_SECRET" ]; then
  echo "Set the Flask secret in conf.env file."
  exit 1
fi

if [ -z "$KEYCLOAK_CLIENT_SECRET" ]; then
  echo "Set the Keycloak client secret in conf.env file."
  exit 1
fi

if [ -z "$IDP_READER_PASSWORD" ]; then
  echo "Set the IdP reader password in conf.env file."
  exit 1
fi

if [ -z "$WEB_GUI_URL" ]; then
  echo "Set the web GUI URL in conf.env file."
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

# Same values as the root create_conf.sh
KEYCLOAK_ISSUER="${KEYCLOAK_ISSUER:-${KEYCLOAK_PUBLIC_URL%/}/realms/${KEYCLOAK_REALM}}"
KEYCLOAK_REDIRECT_URI="${WEB_GUI_URL%/}/api/auth/callback"

mkdir -p $ACCESS_ZONE_KUBE_PATH/volumes


####################################
## REST API SECTION / ACCESS TO SERVICES
####################################
# Values are written between double quotes : a " or a \ in a value of conf.env breaks the file.
cat << EOF > $ACCESS_ZONE_KUBE_PATH/volumes/configmap_flask_env.yml
apiVersion: v1
kind: ConfigMap
metadata:
  name: flask-env
  namespace: datalake
  labels:
    app.kubernetes.io/name: flask-app
    app.kubernetes.io/part-of: access-zone
data:
  FEDERATION_ENABLED: "$FEDERATION_ENABLED"
  KEYCLOAK_URL: "$KEYCLOAK_URL"
  KEYCLOAK_PUBLIC_URL: "$KEYCLOAK_PUBLIC_URL"
  KEYCLOAK_ISSUER: "$KEYCLOAK_ISSUER"
  KEYCLOAK_REALM: "$KEYCLOAK_REALM"
  KEYCLOAK_CLIENT_ID: "$KEYCLOAK_CLIENT_ID"
  KEYCLOAK_REDIRECT_URI: "$KEYCLOAK_REDIRECT_URI"
  KEYCLOAK_IDP_ID: "$KEYCLOAK_IDP_ID"
  KEYCLOAK_PROTOCOL_ID: "$KEYCLOAK_PROTOCOL_ID"
  FEDERATED_PROJECT: "$FEDERATED_PROJECT"
  FEDERATED_DOMAIN: "$FEDERATED_DOMAIN"
  IDP_READER_USER: "$IDP_READER_USER"
  IDP_READER_PROJECT: "service"
  KEYSTONE_URL: "$KEYSTONE_URL"
  WEB_GUI_URL: "$WEB_GUI_URL"
  JUPYTERHUB_PUBLIC_LOGIN_URL: "$JUPYTERHUB_PUBLIC_LOGIN_URL"
  OBJECT_STORAGE_BACKEND: "swift"
  AUTHENTICATION_BACKEND: "openstack"
  S3_ENDPOINT: "http://swift-proxy:8080"
EOF

cat << EOF > $ACCESS_ZONE_KUBE_PATH/volumes/secret_flask_env.yml
apiVersion: v1
kind: Secret
metadata:
  name: flask-env
  namespace: datalake
  labels:
    app.kubernetes.io/name: flask-app
    app.kubernetes.io/part-of: access-zone
type: Opaque
stringData:
  KEYCLOAK_CLIENT_SECRET: "$KEYCLOAK_CLIENT_SECRET"
  IDP_READER_PASSWORD: "$IDP_READER_PASSWORD"
  FLASK_SECRET: "$FLASK_SECRET"
EOF
chmod 600 $ACCESS_ZONE_KUBE_PATH/volumes/secret_flask_env.yml


####################################
## WEB GUI SECTION
####################################
# 'EOF' between quotes : the nginx variables ($uri, $host...) are written as is
cat << 'EOF' > $ACCESS_ZONE_KUBE_PATH/volumes/configmap_web_gui_nginx.yml
apiVersion: v1
kind: ConfigMap
metadata:
  name: web-gui-nginx
  namespace: datalake
  labels:
    app.kubernetes.io/name: web-gui
    app.kubernetes.io/part-of: access-zone
data:
  default.conf: |
    server {
        listen 8080;
        server_name _;
        root /usr/share/nginx/html;

        location = /nginx-health {
            access_log off;
            return 200 "OK";
        }

        # React Router : an unknown path serves index.html, the application routes it
        location / {
            try_files $uri $uri/ /index.html;
        }

        # hashed files of the build : cached by the browser
        location /static/ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
EOF


####################################
## NGINX PROXY SECTION
####################################
# Same conf as access_zone/nginx/conf.d/default.conf, with the Service names instead of the 10.5.x.x IPs.
# /hub/ goes to the proxy of the JupyterHub chart (namespace datalake-jupyter). Its address is resolved at each request
# (resolver + variable) and not once at start : nginx starts even if JupyterHub is missing (/hub/ answers 502 meanwhile),
# and follows a new IP of proxy-public after a reinstall of the chart.
cat << 'EOF' > $ACCESS_ZONE_KUBE_PATH/volumes/configmap_nginx_proxy.yml
apiVersion: v1
kind: ConfigMap
metadata:
  name: nginx-proxy
  namespace: datalake
  labels:
    app.kubernetes.io/name: nginx-proxy
    app.kubernetes.io/part-of: access-zone
data:
  default.conf: |
    server {
        listen 8080;
        server_name _;  # accepte tout

        # Taille max pour les uploads
        client_max_body_size 500M;

        location = /nginx-health {
            access_log off;
            return 200 "OK";
        }

        # 1. Application web principale (défaut sur /)
        location / {
            proxy_pass         http://web-gui:8080;
            proxy_set_header   Host $host;
            proxy_set_header   X-Real-IP $remote_addr;
            proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header   X-Forwarded-Proto $scheme;
            proxy_redirect     off;
        }

        # 2. API Flask → /api/
        location /api/ {
            proxy_pass         http://flask-app:5000/;
            proxy_set_header   Host $host;
            proxy_set_header   X-Real-IP $remote_addr;
            proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header   X-Forwarded-Proto $scheme;

            # Réécrit les URLs renvoyées par Flask si besoin
            sub_filter_once off;
            sub_filter 'href="/' 'href="/api/';
            sub_filter 'src="/'  'src="/api/';
        }

        # 3. JupyterHub → /hub/ (base_url /hub/ in the chart : the path is kept as is)
        location /hub/ {
            # DNS of the cluster (CoreDNS), name looked up again every 10 s ; full Service name : no search domain here
            resolver kube-dns.kube-system.svc.cluster.local valid=10s;
            set $jupyterhub_upstream http://proxy-public.datalake-jupyter.svc.cluster.local:80;
            proxy_pass $jupyterhub_upstream;

            # Headers Websocket (Indispensables)
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";

            # Headers Proxy Standards
            # $http_host and not $host : $host drops the port, and the notebook server compares the Origin of the browser
            # (http://localhost:7000) with Host to accept the websocket of the kernels (Compose : allow_origin = '*' in the image instead)
            proxy_set_header Host $http_host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # Gestion du Scheme pour que Jupyter sache s'il est en https ou http
            proxy_set_header X-Scheme $scheme;

            proxy_buffering off;
        }
    }
EOF
