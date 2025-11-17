// src/utils/s3client.js
import {getAuthData} from "./authUtils";

const API_BASE_URL = 'http://localhost:5000'; // Ajustez si nécessaire

const getAuthHeaders = () => {
  const authData = getAuthData()

  //   const authDataStr = localStorage.getItem('authData');
  // let authData = null;
  // if (authDataStr) {
  //   try {
  //     authData = JSON.parse(authDataStr);
  //   } catch (e) {
  //     console.error('Invalid auth data in storage');
  //   }
  // }
  let token = authData.access_token;
  if (!token) throw new Error('JWT token manquant');
  return {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
  };
};

/**
 * Récupère la liste des buckets.
 * @returns {Promise<Array<{name: string}>>} Liste des buckets.
 */
export const getBuckets = async () => {
  const response = await fetch(API_BASE_URL+`/buckets`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  const data = await response.json();
  console.log(data)
  return data.buckets || [];
};

/**
 * Crée un nouveau bucket avec options avancées.
 * @param {string} bucketName - Nom du bucket.
 * @param {string} [region='us-east-1'] - Région du bucket (défaut: 'us-east-1').
 * @param {Object} [options={}] - Options supplémentaires (ex. { ObjectLocking: true }).
 * @returns {Promise<Object>} Réponse de création.
 */
export const createBucket = async (bucketName, region = 'us-east-1', options = {}) => {
  const response = await fetch(`${API_BASE_URL}/buckets`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({ name: bucketName, region, objectLocking: options.ObjectLocking, ...options }),
  });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
};

/**
 * Supprime un bucket.
 * @param {string} bucketName - Nom du bucket à supprimer.
 * @returns {Promise<Object>} Réponse de suppression.
 */
export const removeBucket = async (bucketName) => {
  const response = await fetch(`${API_BASE_URL}/buckets/${bucketName}`, {
    method: 'DELETE',
    headers: getAuthHeaders(),
  });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
};
/**
 * Liste les objets dans un bucket.
 * @param {string} bucketName - Nom du bucket.
 * @param {string} [prefix=''] - Préfixe pour filtrer.
 * @returns {Promise<Array<{key: string, size: number}>>} Liste des objets.
 */
export const listObjects = async (bucketName, prefix = '') => {
  const response = await fetch(`${API_BASE_URL}/buckets/${bucketName}/objects?prefix=${encodeURIComponent(prefix)}&delimiter=/`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  const data = await response.json();
  console.log("listObjects : DATA.OBJECTS =", data.objects);  // Debug metadata
  return { objects: data.objects || [], prefixes: data.prefixes || [] };
};
/**
 * Upload un fichier dans un bucket.
 * @param {string} bucketName - Nom du bucket.
 * @param {string} key - Chemin de l'objet.
 * @param {File} file - Fichier à uploader.
 * @param {Function} [onProgress] - Callback pour progression.
 * @returns {Promise<Object>} Réponse d'upload.
 */
export const uploadObject = async (bucketName, key, file, onProgress) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('key', key);
  formData.append('contentType', file.type || 'application/octet-stream');
  formData.append('creationDate', new Date().toISOString());  // Pour metadata en backend

  const xhr = new XMLHttpRequest();
  xhr.open('POST', `${API_BASE_URL}/buckets/${bucketName}/objects`);
  xhr.setRequestHeader('Authorization', getAuthHeaders().Authorization);

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
/**
 * Télécharge un objet depuis un bucket.
 * @param {string} bucketName - Nom du bucket.
 * @param {string} key - Chemin de l'objet.
 * @returns {Promise<Blob>} Contenu du fichier sous forme de Blob.
 */
export const downloadObject = async (bucketName, key) => {
  const response = await fetch(`${API_BASE_URL}/buckets/${bucketName}/objects/${encodeURIComponent(key)}`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.blob();
};

/**
 * Supprime un objet dans un bucket.
 * @param {string} bucketName - Nom du bucket.
 * @param {string} key - Chemin de l'objet.
 * @returns {Promise<Object>} Réponse de suppression.
 */
export const deleteObject = async (bucketName, key) => {
  const response = await fetch(`${API_BASE_URL}/buckets/${bucketName}/objects/${encodeURIComponent(key)}`, {
    method: 'DELETE',
    headers: getAuthHeaders(),
  });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
};