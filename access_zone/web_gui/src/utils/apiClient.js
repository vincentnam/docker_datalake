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
