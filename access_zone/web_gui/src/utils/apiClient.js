import { getActiveProject, getAuthData } from './authUtils';

const API_BASE_URL = process.env.REACT_APP_FLASK_APP_URL || 'http://localhost:7000/api';

const buildAuthHeaders = ({ includeJsonContentType = true } = {}) => {
  const authData = getAuthData();
  const token = authData?.access_token;

  if (!token) {
    throw new Error('Utilisateur non authentifie');
  }

  const headers = {
    Authorization: `Bearer ${token}`,
  };
  const project = getActiveProject();
  if (project) {
    headers.Project = project;
  }

  if (includeJsonContentType) {
    headers['Content-Type'] = 'application/json';
  }

  return headers;
};

export const loginWithCredentials = async ({ username, password, project }) => {
  const headers = {
    'X-Username': username,
    'X-Password': password,
  };

  if (project) {
    headers.Project = project;
  }

  const response = await fetch(`${API_BASE_URL}/`, {
    method: 'GET',
    headers,
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || 'Echec de connexion');
  }

  return data;
};

// Finalize a login from an existing Keystone token (e.g. obtained via Keycloak
// SSO). Hits the same `/` endpoint as the password login but with a Bearer
// token, returning the same auth payload shape.
export const loginWithToken = async ({ token, project }) => {
  const headers = {
    Authorization: `Bearer ${token}`,
  };
  if (project) {
    headers.Project = project;
  }

  const response = await fetch(`${API_BASE_URL}/`, {
    method: 'GET',
    headers,
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || 'Echec de connexion SSO');
  }

  return data;
};

// URL the browser is sent to in order to start the Keycloak SSO login.
export const getSsoLoginUrl = () => `${API_BASE_URL}/auth/login`;

// Ask the API whether Keycloak SSO is enabled (to show the SSO button or not).
export const fetchAuthConfig = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/auth/config`);
    if (!response.ok) {
      return { sso_enabled: false };
    }
    return await response.json();
  } catch (e) {
    return { sso_enabled: false };
  }
};

export const apiFetch = async (path, options = {}) => {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      ...buildAuthHeaders({ includeJsonContentType: !(options.body instanceof FormData) }),
      ...(options.headers || {}),
    },
  });

  return response;
};

export const getApiBaseUrl = () => API_BASE_URL;
