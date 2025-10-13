import mc from "./mc";
import prettyBytes from "pretty-bytes";
import { orderBy } from "lodash";

const getAsNode = (objectInfo) => {
  const { name = "", pathName = "", displayKey, leaf, children, size, ...dataKeys } = objectInfo;

  return {
    ...objectInfo,
    key: `${pathName}${name}`.replace(/\/+/g, "/"), // Normaliser les barres obliques
    data: {
      ...dataKeys,
      name: displayKey,
      size: size > 0 ? prettyBytes(size) : "",
      rawSize: size,
    },
    leaf: leaf,
    children: children,
  };
};

export const listObjectsOfPrefix = (bName, pathName = "") => {
  return new Promise((resolve, reject) => {
    let objList = [];
    const seenKeys = new Set();

    try {
      // Normaliser le préfixe pour MinIO (barre oblique finale si non vide)
      const normalizedPath = pathName ? `${pathName.replace(/^\/+|\/+$/g, "")}/` : "";
      // console.log(`listObjectsOfPrefix: bucket=${bName}, prefix=${normalizedPath}`);

      const objectsStream = mc.extensions.listObjectsV2WithMetadata(bName, normalizedPath, false, "");

      objectsStream.on("data", (chunk) => {
        const { name: objectName = "", prefix = "", size = 0, lastModified, contentType } = chunk;
        const isFolder = prefix || objectName.endsWith("/");
        // console.log(chunk);
        // console.log("cunk");
        // Nom effectif (préfixe pour dossiers, nom pour fichiers)
        const effectiveName = prefix || objectName;
        if (!effectiveName) {
          console.log("Ignorer chunk invalide:", chunk);
          return;
        }

        // Ignorer l'objet si c'est le préfixe lui-même
        if (effectiveName === normalizedPath || (isFolder && effectiveName.replace(/\/+$/, "") === normalizedPath.replace(/\/+$/, ""))) {
          console.log(`Ignorer préfixe lui-même: ${effectiveName}`);
          return;
        }

        // Calculer le nom d'affichage (partie après le préfixe)
        let displayKey = effectiveName.replace(/^\/+|\/+$/g, "");
        if (normalizedPath && displayKey.startsWith(normalizedPath)) {
          displayKey = displayKey.substring(normalizedPath.length);
        }
        if (isFolder && displayKey.endsWith("/")) {
          displayKey = displayKey.substring(0, displayKey.length - 1);
        }
        if (!displayKey) {
          console.log("displayKey vide, ignoré:", chunk);
          return;
        }

        // Clé unique pour éviter les doublons
        const nodeKey = `${normalizedPath}${displayKey}`.replace(/\/+/g, "/");
        if (seenKeys.has(nodeKey)) {
          console.log(`Ignorer doublon: ${nodeKey}`);
          return;
        }
        seenKeys.add(nodeKey);

        const nodeInfo = getAsNode({
          ...chunk,
          name: displayKey,
          displayKey: displayKey,
          pathName: normalizedPath,
          size,
          lastModified,
          contentType,
          children: isFolder ? [] : undefined, // Dossiers ont children vide
          leaf: !isFolder,
        });

        objList.push(nodeInfo);
      });

      objectsStream.on("error", (err) => {
        console.error("Erreur dans objectsStream:", err);
        reject([]);
      });

      objectsStream.on("end", () => {
        console.log(`listObjectsOfPrefix terminé: ${objList.length} objets`, objList);
        resolve(orderBy(objList, ["leaf", "data.name"], ["asc", "asc"]));
      });
    } catch (err) {
      console.error("Erreur dans listObjectsOfPrefix:", err);
      reject([]);
    }
  });
};

export const loadObjectList = async (bucketName, path) => {
  try {
    const objList = await listObjectsOfPrefix(bucketName, path || "");
    return orderBy(objList, ["leaf", "data.name"], ["asc", "asc"]);
  } catch (err) {
    console.error("Erreur dans loadObjectList:", err);
    throw new Error("Impossible de charger la liste des objets.");
  }
};

export const createFolder = async (bucketName, prefixPath, folderName) => {
  const folderPath = `${prefixPath ? prefixPath.replace(/\/+$/, "") + "/" : ""}${folderName}/`.replace(/\/+/g, "/");
  await mc.putObject(bucketName, folderPath, "", {
    "Content-Type": "application/x-directory",
  });
};