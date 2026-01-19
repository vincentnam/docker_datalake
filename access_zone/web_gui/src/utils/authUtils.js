export const getAuthData = () => {
  const authDataStr = localStorage.getItem('authData');
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
    localStorage.setItem('authData', JSON.stringify(data));
  } catch (e) {
    console.error('Error storing auth data', e);
  }
};