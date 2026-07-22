const DEFAULT_JUPYTERHUB_URL = '/hub/hub/user-redirect/tree';
const JUPYTER_SERVER_WAIT_SECONDS = 120;

export const getJupyterHubUrl = () => {
  const configuredUrl = process.env.REACT_APP_JUPYTERHUB_URL?.trim();

  // La route relative permet de rester sur le host actuel avec la conf par défaut.
  if (!configuredUrl || configuredUrl === 'URL_CHANGEME') {
    return DEFAULT_JUPYTERHUB_URL;
  }

  return configuredUrl;
};

const getCookieValue = (cookieName) => {
  const cookie = document.cookie
    .split('; ')
    .find((currentCookie) => currentCookie.startsWith(`${cookieName}=`));
  return cookie ? decodeURIComponent(cookie.split('=', 2)[1]) : '';
};

const getNotebookFilename = (objectKey) => {
  const objectName = objectKey.split('/').pop() || 'data';
  const safeObjectName = objectName
    .replace(/[^a-zA-Z0-9._-]+/g, '-')
    .replace(/^[.-]+|[.-]+$/g, '') || 'data';
  return `download-${safeObjectName}-${Date.now()}.ipynb`;
};

const buildFirstCell = (bucketName, objectKey) => {
  const cellTemplate = `import time
from getpass import getpass
from pathlib import Path
from urllib.parse import quote

import requests
from IPython.display import HTML, display

FLASK_URL = "http://flask-app:5000"
BUCKET_NAME = __BUCKET_NAME__
OBJECT_KEY = __OBJECT_KEY__


def login_with_local_account():
    username = input("Utilisateur Keystone : ").strip()
    password = getpass("Mot de passe : ")
    project_name = input("Projet : ").strip()

    response = requests.get(
        f"{FLASK_URL}/",
        headers={
            "X-Username": username,
            "X-Password": password,
            "Project": project_name,
        },
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def login_with_sso():
    configuration_response = requests.get(
        f"{FLASK_URL}/auth/config",
        timeout=30,
    )
    configuration_response.raise_for_status()
    identity_providers = configuration_response.json().get("idps", [])
    if not identity_providers:
        raise RuntimeError("Aucun fournisseur d'identité fédéré n'est disponible")

    for index, identity_provider in enumerate(identity_providers, start=1):
        description = identity_provider.get("description") or identity_provider["id"]
        print(f"{index}. {description}")

    selected_index = int(input("Fournisseur d'identité : ")) - 1
    selected_identity_provider = identity_providers[selected_index]

    start_response = requests.post(
        f"{FLASK_URL}/auth/notebook/sso/start",
        json={"identity_provider": selected_identity_provider["id"]},
        timeout=30,
    )
    start_response.raise_for_status()
    authentication_request = start_response.json()

    display(HTML(
        f'<a href="{authentication_request["login_url"]}" target="_blank">'
        "Ouvrir la connexion SSO"
        "</a>"
    ))
    print("Terminez la connexion dans le navigateur...")

    while True:
        status_response = requests.post(
            f"{FLASK_URL}/auth/notebook/sso/status",
            json={
                "request_id": authentication_request["request_id"],
                "polling_secret": authentication_request["polling_secret"],
            },
            timeout=30,
        )
        status_response.raise_for_status()
        authentication_status = status_response.json()

        if authentication_status["status"] == "complete":
            return authentication_status
        if authentication_status["status"] == "error":
            raise RuntimeError(authentication_status.get("error") or "Échec de la connexion SSO")
        time.sleep(2)


def download_object(authentication):
    access_token = authentication["access_token"]
    project_name = authentication.get("project_name") or authentication.get("user", {}).get("project_name")
    destination = Path(OBJECT_KEY).name

    headers = {"Authorization": f"Bearer {access_token}"}
    if project_name:
        headers["Project"] = project_name

    response = requests.get(
        f"{FLASK_URL}/buckets/{quote(BUCKET_NAME, safe='')}/objects/{quote(OBJECT_KEY, safe='')}",
        headers=headers,
        timeout=300,
    )
    response.raise_for_status()
    Path(destination).write_bytes(response.content)
    print(f"Fichier téléchargé : {destination}")


authentication_mode = input("Connexion locale ou SSO ? [local/sso] : ").strip().lower()
authentication = login_with_sso() if authentication_mode == "sso" else login_with_local_account()
download_object(authentication)
`;

  // JSON.stringify produit aussi une chaîne Python valide pour ces deux valeurs.
  return cellTemplate
    .replace('__BUCKET_NAME__', JSON.stringify(bucketName))
    .replace('__OBJECT_KEY__', JSON.stringify(objectKey));
};

const buildNotebook = (bucketName, objectKey) => ({
  cells: [
    {
      cell_type: 'code',
      execution_count: null,
      metadata: {},
      outputs: [],
      source: buildFirstCell(bucketName, objectKey).split(/(?<=\n)/),
    },
  ],
  metadata: {
    kernelspec: {
      display_name: 'Python 3',
      language: 'python',
      name: 'python3',
    },
    language_info: {
      name: 'python',
      version: '3',
    },
  },
  nbformat: 4,
  nbformat_minor: 5,
});

const wait = (milliseconds) => new Promise((resolve) => {
  window.setTimeout(resolve, milliseconds);
});

export const createNotebookInJupyter = async ({ username, bucketName, objectKey }) => {
  const notebookFilename = getNotebookFilename(objectKey);
  const encodedUsername = encodeURIComponent(username);
  const encodedNotebookFilename = encodeURIComponent(notebookFilename);
  const contentsUrl = `/hub/user/${encodedUsername}/api/contents/${encodedNotebookFilename}`;
  const notebookUrl = `/hub/user/${encodedUsername}/lab/tree/${encodedNotebookFilename}`;
  const deadline = Date.now() + (JUPYTER_SERVER_WAIT_SECONDS * 1000);

  while (Date.now() < deadline) {
    const xsrfToken = getCookieValue('_xsrf');
    const response = await fetch(contentsUrl, {
      method: 'PUT',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        ...(xsrfToken ? { 'X-XSRFToken': xsrfToken } : {}),
      },
      body: JSON.stringify({
        type: 'notebook',
        format: 'json',
        content: buildNotebook(bucketName, objectKey),
      }),
    });

    const contentType = response.headers.get('Content-Type') || '';
    if (response.ok && contentType.includes('application/json')) {
      return notebookUrl;
    }

    // Le popup JupyterHub peut encore être sur le login ou en train de spawn.
    if (response.status >= 500 || response.status === 404 || response.redirected) {
      await wait(2000);
      continue;
    }

    throw new Error(`JupyterHub a refusé la création du notebook (HTTP ${response.status})`);
  }

  throw new Error('Le serveur JupyterHub ne répond pas après deux minutes');
};
