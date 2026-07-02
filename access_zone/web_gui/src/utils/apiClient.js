import { getActiveProject, getActiveProjectId, getAuthData } from './authUtils';

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
  // Domain-agnostic project reference, preferred by the API over the name.
  const projectId = getActiveProjectId();
  if (projectId) {
    headers['Project-Id'] = projectId;
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
export const loginWithToken = async ({ token, project, projectId }) => {
  const headers = {
    Authorization: `Bearer ${token}`,
  };
  if (project) {
    headers.Project = project;
  }
  if (projectId) {
    headers['Project-Id'] = projectId;
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

// Log out : ask the API to REVOKE the current Keystone token server-side so it
// can no longer be used, in addition to clearing the local browser state.
// Best-effort : never block the UI logout on a network/revocation error.
export const logout = async () => {
  const authData = getAuthData();
  const token = authData?.access_token;
  if (!token) {
    return { revoked: false };
  }
  try {
    const response = await fetch(`${API_BASE_URL}/auth/logout`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!response.ok) {
      return { revoked: false };
    }
    return await response.json();
  } catch (e) {
    console.error('Logout revocation failed', e);
    return { revoked: false };
  }
};

// URL the browser is sent to in order to start the SSO login on one of the
// identity providers registered in Keystone (see fetchAuthConfig).
export const getSsoLoginUrl = (idpId) =>
  `${API_BASE_URL}/auth/login${idpId ? `?idp=${encodeURIComponent(idpId)}` : ''}`;

// URL of the full-page logout navigation : Flask closes the Keycloak SSO
// session (so another account can log in) then redirects to the login page.
export const getSsoLogoutUrl = () => `${API_BASE_URL}/auth/logout`;

// Login options : whether SSO is enabled, and the list of identity providers
// registered in Keystone ([{id, description, login_url}]) — one login button
// per entry, next to the local (password) login.
export const fetchAuthConfig = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/auth/config`);
    if (!response.ok) {
      return { sso_enabled: false, idps: [] };
    }
    const data = await response.json();
    return { sso_enabled: Boolean(data.sso_enabled), idps: data.idps || [] };
  } catch (e) {
    return { sso_enabled: false, idps: [] };
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
