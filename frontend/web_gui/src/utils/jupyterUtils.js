import axios from 'axios';

const JUPYTERHUB_URL = process.env.REACT_APP_JUPYTERHUB_URL || 'http://localhost:8000';
const JUPYTERHUB_TOKEN = process.env.REACT_APP_JUPYTERHUB_TOKEN || '';

const getJupyterHubApiUrl = () => `${JUPYTERHUB_URL}/hub/api`;
const getUserServerApiUrl = (username) => `${JUPYTERHUB_URL}/user/${username}/api`;

export const checkJupyterServer = async (username) => {
  try {
    const response = await axios.get(`${getJupyterHubApiUrl()}/users/${username}`, {
      headers: {
        Authorization: `token ${JUPYTERHUB_TOKEN}`,
      },
    });
    return response.data.servers && Object.keys(response.data.servers).length > 0;
  } catch (err) {
    if (err.response?.status === 404) {
      return false;
    }
    throw new Error(`Erreur lors de la vérification du serveur JupyterHub : ${err.response?.data?.message || err.message}`);
  }
};

export const startJupyterServer = async (username) => {
  try {
    const response = await axios.post(
      `${getJupyterHubApiUrl()}/users/${username}/server`,
      {},
      {
        headers: {
          Authorization: `token ${JUPYTERHUB_TOKEN}`,
        },
      }
    );
    return response.status === 201 || response.status === 202;
  } catch (err) {
    throw new Error(`Échec du lancement du serveur JupyterHub : ${err.response?.data?.message || err.message}`);
  }
};

export const listNotebooks = async (username, path = '') => {
  try {
    const apiUrl = `${getUserServerApiUrl(username)}/contents/${path}`;
    const response = await axios.get(apiUrl, {
      headers: {
        Authorization: `token ${JUPYTERHUB_TOKEN}`,
      },
    });
    return response.data.content;
  } catch (err) {
    throw new Error(`Erreur lors de la récupération des notebooks : ${err.response?.data?.message || err.message}`);
  }
};

export const getNotebookContent = async (username, path) => {
  try {
    const apiUrl = `${getUserServerApiUrl(username)}/contents/${path}`;
    const response = await axios.get(apiUrl, {
      headers: {
        Authorization: `token ${JUPYTERHUB_TOKEN}`,
      },
    });
    if (response.data.type === 'notebook') {
      return response.data.content;
    } else {
      throw new Error('Le chemin spécifié n\'est pas un notebook');
    }
  } catch (err) {
    throw new Error(`Erreur lors de la récupération du contenu du notebook : ${err.response?.data?.message || err.message}`);
  }
};

export const getOrCreateSession = async (username, path) => {
  try {
    const apiUrl = `${getUserServerApiUrl(username)}/sessions`;
    const sessionsResponse = await axios.get(apiUrl, {
      headers: {
        Authorization: `token ${JUPYTERHUB_TOKEN}`,
      },
    });
    const sessions = sessionsResponse.data;
    const existingSession = sessions.find(session => session.path === path);
    if (existingSession) {
      return existingSession;
    }
    const createResponse = await axios.post(apiUrl, {
      path: path,
      type: 'notebook',
    }, {
      headers: {
        Authorization: `token ${JUPYTERHUB_TOKEN}`,
      },
    });
    return createResponse.data;
  } catch (err) {
    throw new Error(`Erreur lors de la gestion de la session : ${err.response?.data?.message || err.message}`);
  }
};

export const getKernelWebSocketUrl = (username, kernelId) => {
  return `ws://${new URL(JUPYTERHUB_URL).host}/user/${username}/api/kernels/${kernelId}/channels?token=${JUPYTERHUB_TOKEN}`;
};

export const createNotebook = async (username, notebookName, content) => {
  const apiUrl = `${JUPYTERHUB_URL}/user/${username}/api/contents/${notebookName}.ipynb`;
  try {
    const response = await axios.put(
      apiUrl,
      { type: "notebook", content },
      { headers: { Authorization: `token ${JUPYTERHUB_TOKEN}` } }
    );
    return response.data;
  } catch (err) {
    throw new Error(`Erreur lors de la création du notebook : ${err.message}`);
  }
};

export const getNotebookUrl = (username, notebookName) => {
  return `${JUPYTERHUB_URL}/user/${username}/notebooks/${notebookName}.ipynb`;
};