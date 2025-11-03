// import mc from ".//mc";
import { downloadObject } from './s3client';
export const downloadFile = async (bucketName, path, filename) => {
  try {
    const blob = await downloadObject(bucketName, path);  // Fetch blob via proxy sécurisé
    console.log("COUCOU LE BLOB")
    console.log(blob)
    const url = URL.createObjectURL(blob);  // URL locale temporaire
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;  // Force téléchargement avec nom
    link.target = "_self";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);  // Cleanup pour éviter memory leak
  } catch (err) {
    console.error("Erreur download:", err);  // Log pour debug
    throw new Error("Impossible de télécharger le fichier: " + err.message);
  }
};

export const moveObject = async (bucketName, sourceKey, targetFolderKey) => {
  try {
    const filename = sourceKey.split("/").pop();
    const destinationKey = `${targetFolderKey}/${filename}`.replace(/\/+/g, "/");
    // await mc.copyObject(bucketName, sourceKey, destinationKey);
    // await mc.removeObject(bucketName, sourceKey);
  } catch (err) {
    throw new Error("Impossible de déplacer le fichier.");
  }
};