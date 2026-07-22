const DEFAULT_JUPYTERHUB_URL = '/hub/hub/user-redirect/tree';

export const getJupyterHubUrl = () => {
  const configuredUrl = process.env.REACT_APP_JUPYTERHUB_URL?.trim();

  // La route relative permet de rester sur le host actuel avec la conf par défaut.
  if (!configuredUrl || configuredUrl === 'URL_CHANGEME') {
    return DEFAULT_JUPYTERHUB_URL;
  }

  return configuredUrl;
};
