import mc from ".//mc";

export const downloadFile = async (bucketName, path, filename) => {
  try {
    const signedUrl = await mc.presignedGetObject(bucketName, path, 60, {
      "response-content-disposition": `attachment; filename="${filename}"`,
    });
    const link = document.createElement("a");
    link.href = signedUrl;
    link.target = "_self";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  } catch (err) {
    throw new Error("Impossible de télécharger le fichier");
  }
};

export const moveObject = async (bucketName, sourceKey, targetFolderKey) => {
  try {
    const filename = sourceKey.split("/").pop();
    const destinationKey = `${targetFolderKey}/${filename}`.replace(/\/+/g, "/");
    await mc.copyObject(bucketName, sourceKey, destinationKey);
    await mc.removeObject(bucketName, sourceKey);
  } catch (err) {
    throw new Error("Impossible de déplacer le fichier.");
  }
};