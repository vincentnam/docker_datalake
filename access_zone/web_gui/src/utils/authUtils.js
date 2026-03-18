export const AUTH_DATA_KEY = 'authData';
export const ACTIVE_PROJECT_KEY = 'activeProject';
const CREDENTIALS_KEY = 'sessionCredentials';

export const getAuthData = () => {
  const authDataStr = localStorage.getItem(AUTH_DATA_KEY);
  if (!authDataStr) {
    return null;
  }

  try {
    return JSON.parse(authDataStr);
  } catch (e) {
    console.error('Invalid auth data in storage');
    return null;
  }
};

export const setAuthData = (data) => {
  try {
    localStorage.setItem(AUTH_DATA_KEY, JSON.stringify(data));
  } catch (e) {
    console.error('Error storing auth data', e);
  }
};

export const clearAuthData = () => {
  localStorage.removeItem(AUTH_DATA_KEY);
  localStorage.removeItem(ACTIVE_PROJECT_KEY);
  sessionStorage.removeItem(CREDENTIALS_KEY);
};

export const getAvailableProjects = () => {
  const authData = getAuthData();
  const projects = authData?.user?.projects || authData?.projects || [];
  return Array.isArray(projects) ? projects : [];
};

export const getActiveProject = () => {
  const savedProject = localStorage.getItem(ACTIVE_PROJECT_KEY);
  if (savedProject) {
    return savedProject;
  }

  const authData = getAuthData();
  return authData?.user?.project_name || '';
};

export const setActiveProject = (projectName) => {
  if (!projectName) {
    return;
  }
  localStorage.setItem(ACTIVE_PROJECT_KEY, projectName);
};

export const setSessionCredentials = (username, password) => {
  try {
    sessionStorage.setItem(CREDENTIALS_KEY, JSON.stringify({ username, password }));
  } catch (e) {
    console.error('Error storing session credentials', e);
  }
};

export const getSessionCredentials = () => {
  const credentialsStr = sessionStorage.getItem(CREDENTIALS_KEY);
  if (!credentialsStr) {
    return null;
  }

  try {
    return JSON.parse(credentialsStr);
  } catch (e) {
    console.error('Invalid session credentials in storage');
    return null;
  }
};
