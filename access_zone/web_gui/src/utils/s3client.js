import { apiFetch, getApiBaseUrl } from './apiClient';
import { getActiveProject, getAuthData } from './authUtils';

const API_BASE_URL = getApiBaseUrl();

const assertAuthenticated = () => {
  const token = getAuthData()?.access_token;
  if (!token) {
    throw new Error('Token d\'authentification manquant');
  }
};

export const getBuckets = async () => {
  assertAuthenticated();
  const response = await apiFetch('/buckets', { method: 'GET' });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);

  const data = await response.json();
  return data.buckets || [];
};

export const createBucket = async (bucketName) => {
  assertAuthenticated();
  const safeBucketName = encodeURIComponent(bucketName);
  const response = await apiFetch(`/buckets/${safeBucketName}`, {
    method: 'POST',
    body: JSON.stringify({}),
  });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);

  return response.json();
};

export const removeBucket = async (bucketName) => {
  assertAuthenticated();
  const safeBucketName = encodeURIComponent(bucketName);
  const response = await apiFetch(`/buckets/${safeBucketName}`, {
    method: 'DELETE',
  });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);

  return response.json();
};

export const listObjects = async (bucketName, prefix = '') => {
  assertAuthenticated();
  const safeBucketName = encodeURIComponent(bucketName);
  const response = await apiFetch(
    `/buckets/${safeBucketName}/objects?prefix=${encodeURIComponent(prefix)}&delimiter=/`,
    {
      method: 'GET',
    }
  );

  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  const data = await response.json();
  return { objects: data.objects || [], prefixes: data.prefixes || [] };
};

export const uploadObject = async (bucketName, key, file, onProgress) => {
  assertAuthenticated();
  const authData = getAuthData();

  const formData = new FormData();
  formData.append('file', file);
  formData.append('key', key);
  formData.append('contentType', file.type || 'application/octet-stream');

  const xhr = new XMLHttpRequest();
  xhr.open('POST', `${API_BASE_URL}/buckets/${encodeURIComponent(bucketName)}/objects`);
  xhr.setRequestHeader('Authorization', `Bearer ${authData.access_token}`);
  xhr.setRequestHeader('Project', getActiveProject());

  if (onProgress) {
    xhr.upload.onprogress = (event) => {
      if (event.lengthComputable) onProgress((event.loaded / event.total) * 100);
    };
  }

  return new Promise((resolve, reject) => {
    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) resolve(JSON.parse(xhr.responseText));
      else reject(new Error(`HTTP ${xhr.status}`));
    };
    xhr.onerror = reject;
    xhr.send(formData);
  });
};

export const downloadObject = async (bucketName, key) => {
  assertAuthenticated();
  const response = await apiFetch(
    `/buckets/${encodeURIComponent(bucketName)}/objects/${encodeURIComponent(key)}`,
    { method: 'GET' }
  );
  if (!response.ok) throw new Error(`HTTP ${response.status}`);

  return response.blob();
};

export const deleteObject = async (bucketName, key) => {
  assertAuthenticated();
  const response = await apiFetch(
    `/buckets/${encodeURIComponent(bucketName)}/objects/${encodeURIComponent(key)}`,
    {
      method: 'DELETE',
    }
  );
  if (!response.ok) throw new Error(`HTTP ${response.status}`);

  return response.json();
};
