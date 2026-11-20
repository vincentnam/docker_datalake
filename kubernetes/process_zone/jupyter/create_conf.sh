#!/bin/bash


export $(grep -v '^#' ./conf.env | sed 's/\r$//' | xargs)
JUPYTER_PATH="./process_zone/jupyter"
JUPYTER_KUBE_PATH="./kubernetes/process_zone/jupyter"

if [ -z "$JUPYTERHUB_CHART_VERSION" ]; then
  echo "Set the JupyterHub chart version in conf.env file."
  exit 1
fi

if [ -z "$JUPYTERHUB_NOTEBOOK_IMAGE" ]; then
  echo "Set the JupyterHub notebook image in conf.env file."
  exit 1
fi

if [ -z "$JUPYTERHUB_NOTEBOOK_TAG" ]; then
  echo "Set the JupyterHub notebook image tag in conf.env file."
  exit 1
fi

if [ -z "$JUPYTERHUB_STORAGE_SIZE" ]; then
  echo "Set the JupyterHub disk size in conf.env file."
  exit 1
fi

if [ -z "$JUPYTERHUB_USER_STORAGE" ]; then
  echo "Set the JupyterHub user storage in conf.env file."
  exit 1
fi

if [ -z "$JUPYTERHUB_ADMIN" ]; then
  echo "Set the JupyterHub admin username in conf.env file."
  exit 1
fi

# The hub runs in the datalake-jupyter namespace : Flask is reached by its full Service name
FLASK_URL="http://flask-app.datalake.svc.cluster.local:5000"

# The disk request is 90 % of the disk size : the filesystem keeps a part of the disk
JUPYTERHUB_STORAGE_REQUEST="$(( $(numfmt --from=auto "${JUPYTERHUB_STORAGE_SIZE%B}") * 9 / 10 / 1048576 ))Mi"

mkdir -p $JUPYTER_KUBE_PATH/volumes


###################################
# JUPYTERHUB (Zero to JupyterHub chart)
###################################
# Installed by k3s itself (HelmChart object, like Traefik) : no helm tool needed.
# Values of the chart : https://z2jh.jupyter.org/en/stable/resources/reference.html
# The Flask authenticator and its login templates come from the service folder ($JUPYTER_PATH),
# mounted in the hub image of the chart (hub.extraFiles) : no hub image to build.
cat << EOF > $JUPYTER_KUBE_PATH/volumes/helmchart_jupyterhub.yml
apiVersion: helm.cattle.io/v1
kind: HelmChart
metadata:
  name: jupyterhub
  namespace: kube-system
spec:
  repo: https://hub.jupyter.org/helm-chart/
  chart: jupyterhub
  version: "$JUPYTERHUB_CHART_VERSION"
  targetNamespace: datalake-jupyter
  createNamespace: false
  valuesContent: |-
    hub:
      baseUrl: /hub/
      db:
        type: sqlite-pvc
        pvc:
          storageClassName: jupyterhub-disks
          storage: $JUPYTERHUB_STORAGE_REQUEST
      extraFiles:
        datalake-authenticator:
          mountPath: /usr/local/etc/jupyterhub/datalake/datalake_authenticator.py
          stringData: |
$(sed -e 's/\r$//' -e 's/^/            /' $JUPYTER_PATH/datalake_authenticator.py)
        datalake-login-template:
          mountPath: /usr/local/etc/jupyterhub/datalake/templates/login.html
          stringData: |
$(sed -e 's/\r$//' -e 's/^/            /' $JUPYTER_PATH/templates/login.html)
        datalake-native-login-template:
          mountPath: /usr/local/etc/jupyterhub/datalake/templates/native-login.html
          stringData: |
$(sed -e 's/\r$//' -e 's/^/            /' $JUPYTER_PATH/templates/native-login.html)
      extraConfig:
        datalake: |
          import sys
          sys.path.insert(0, "/usr/local/etc/jupyterhub/datalake")
          from datalake_authenticator import FlaskLocalAuthenticator
          c.JupyterHub.authenticator_class = FlaskLocalAuthenticator
          c.JupyterHub.template_paths = ["/usr/local/etc/jupyterhub/datalake/templates"]
          c.FlaskLocalAuthenticator.flask_base_url = "$FLASK_URL"
          c.Authenticator.admin_users = {"$JUPYTERHUB_ADMIN"}
          c.Authenticator.allow_all = True
      networkPolicy:
        egress:                             # the hub calls Flask to authenticate the users
          - to:
              - namespaceSelector:
                  matchLabels:
                    kubernetes.io/metadata.name: datalake
                podSelector:
                  matchLabels:
                    app.kubernetes.io/name: flask-app
            ports:
              - port: 5000
    proxy:
      service:
        type: ClusterIP                     # reached by nginx-proxy (/hub/), never from outside
    singleuser:
      cloudMetadata:
        blockWithIptables: false            # the iptables init container needs privileged + NET_ADMIN, refused by Pod Security :
                                            # the cloud metadata server (169.254.169.254) stays blocked by the NetworkPolicy of the notebooks
      extraEnv:
        DATALAKE_FLASK_URL: "$FLASK_URL"    # read by the consumption code copied from the web GUI (Flask is in another namespace)
      image:
        name: $JUPYTERHUB_NOTEBOOK_IMAGE
        tag: "$JUPYTERHUB_NOTEBOOK_TAG"
      storage:
        type: dynamic
        capacity: $JUPYTERHUB_USER_STORAGE
        dynamic:
          storageClass: jupyter-users
      networkPolicy:
        egress:                             # private IPs are blocked by the chart : only Flask and the Swift proxy are opened
          - to:                             # Flask (SSO ticket of the notebooks)
              - namespaceSelector:
                  matchLabels:
                    kubernetes.io/metadata.name: datalake
                podSelector:
                  matchLabels:
                    app.kubernetes.io/name: flask-app
            ports:
              - port: 5000
          - to:                             # Swift proxy : the data, with the Keystone token of the user (catalog URL)
              - namespaceSelector:
                  matchLabels:
                    kubernetes.io/metadata.name: datalake
                podSelector:
                  matchLabels:
                    app.kubernetes.io/name: swift
                    app.kubernetes.io/component: proxy
            ports:
              - port: 8080
EOF
chmod 600 $JUPYTER_KUBE_PATH/volumes/helmchart_jupyterhub.yml
