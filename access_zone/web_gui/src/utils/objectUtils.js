import prettyBytes from "pretty-bytes";
import { orderBy } from "lodash";
import { listObjects, uploadObject } from "../utils/s3client"; // Ajustez le chemin d'import
const getAsNode = (objectInfo) => {
  const {
    key = "",
    prefix = "",
    displayKey,
    leaf,
    children,
    size,
    lastModified,
    contentType,
    creationDate,
    metadata = {},
    eTag,
    storageClass,
    ...dataKeys
  } = objectInfo;

  console.log(metadata)
  return {
    ...objectInfo,
    key: key || prefix,
    data: {
      ...dataKeys,
      name: displayKey || key.split('/').pop() || 'unknown',
      size: size > 0 ? prettyBytes(size) : (leaf ? '0 B' : '-'),
      rawSize: size || 0,
      lastModified: lastModified ? (typeof lastModified === 'string' ? lastModified : lastModified.toISOString()) : null,
      creationDate: creationDate || metadata?.CreationDate || null,
      contentType: contentType || 'application/octet-stream',
      metadata: metadata,  // Dict complet
      eTag,  // Ajout pour complétude
      storageClass: storageClass || 'STANDARD',
    },
    leaf,
    children,
  };
};
export const listObjectsOfPrefix = async (bucketName, pathName = "") => {
  try {
    // Normaliser le préfixe
    const normalizedPath = pathName ? `${pathName.replace(/^\/+|\/+$/g, "")}/` : "";

    // Fetch depuis API
    const response = await listObjects(bucketName, normalizedPath);
    console.log("response: ", response);
    let { objects = [], prefixes = [] } = response;  // Fallback array vide si undefined

    // Garde-fou : Assurer arrays
    if (!Array.isArray(objects)) objects = [];
    if (!Array.isArray(prefixes)) prefixes = [];

    const objList = [];
    const seenKeys = new Set();

    // Transformer objets (fichiers) en nœuds
    for (const obj of objects) {  // Retiré || [] car déjà fallback
      const { key: objectKey = "", eTag, size = 0, lastModified, contentType, creationDate, metadata = {} } = obj;

      console.log("object : ", obj)

      if (!objectKey || seenKeys.has(objectKey)) continue;
      seenKeys.add(objectKey);

      const isFolder = objectKey.endsWith("/");
      const displayKey = objectKey.replace(normalizedPath, '').replace(/^\/+|\/+$/g, "");
      if (!displayKey) continue;

      objList.push(getAsNode({
        key: objectKey,
        name: displayKey,
        displayKey,
        pathName: normalizedPath,
        size,
        eTag,
        lastModified,
        contentType,
        creationDate:metadata.creationdate,
        metadata,
        leaf: !isFolder,
        children: isFolder ? [] : undefined,
      }));
    }

    // Transformer prefixes (dossiers) en nœuds
    for (const p of prefixes) {
      const { prefix: folderPrefix } = p;
      if (!folderPrefix || seenKeys.has(folderPrefix)) continue;
      seenKeys.add(folderPrefix);

      const displayKey = folderPrefix.replace(normalizedPath, '').replace(/\/+$/, '');
      if (!displayKey) continue;

      objList.push(getAsNode({
        key: folderPrefix,
        name: displayKey,
        displayKey,
        pathName: normalizedPath,
        leaf: false,
        children: [],
        contentType: 'folder',
        metadata: {},
      }));
    }

    console.log(`listObjectsOfPrefix: ${objList.length} nodes générés`);  // Debug
    return orderBy(objList, ["leaf", "data.name"], ["asc", "asc"]);
  } catch (err) {
    console.error("Erreur dans listObjectsOfPrefix:", err);
    return [];
  }
};

export const loadObjectList = async (bucketName, path) => {
  try {
    const objList = await listObjectsOfPrefix(bucketName, path || "");
    console.log("OBJLIST : ", objList)
    return orderBy(objList, ["leaf", "data.name"], ["asc", "asc"]);
  } catch (err) {
    console.error("Erreur dans loadObjectList:", err);
    throw new Error("Impossible de charger la liste des objets.");
  }
};

export const createFolder = async (bucketName, prefixPath, folderName) => {
  const folderPath = `${prefixPath ? prefixPath.replace(/\/+$/, "") + "/" : ""}${folderName}/`.replace(/\/+/g, "/");
  const emptyBlob = new Blob([], { type: "application/x-directory" });
  await uploadObject(bucketName, folderPath, emptyBlob);
};