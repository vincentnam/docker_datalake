import { useState } from "react";
import { uploadObject } from "../utils/s3client";

const useDragAndDrop = (bucketName, prefixPath, loadBucketObjects, toastRef) => {
  const [uploadProgress, setUploadProgress] = useState({});
  const [showProgressDialog, setShowProgressDialog] = useState(false);

  const showSuccess = (message) => {
    toastRef.current.show({ severity: "success", summary: "Succès", detail: message, life: 3000 });
  };

  const showError = (message) => {
    toastRef.current.show({ severity: "error", summary: "Erreur", detail: message, life: 3000 });
  };

  const onDrop = async (acceptedFiles) => {
    setShowProgressDialog(true);
    const filesList = Array.from(acceptedFiles);
    const progressUpdates = {};
    filesList.forEach((file) => {
      progressUpdates[file.name] = { progress: 0, status: "uploading" };
    });
    setUploadProgress(progressUpdates);

    for (const file of filesList) {
      try {
        const filePath = `${prefixPath ? prefixPath.replace(/\/+$/, "") + "/" : ""}${file.name}`.replace(/\/+/g, "/");
        const uploadDate = new Date().toISOString();

        await uploadObject(bucketName, filePath, file, (progress) => {
          setUploadProgress((prev) => ({
            ...prev,
            [file.name]: { ...prev[file.name], progress },
          }));
        });

        setUploadProgress((prev) => ({
          ...prev,
          [file.name]: { progress: 100, status: "completed" },
        }));
        showSuccess(`Fichier ${file.name} téléversé avec succès`);
      } catch (err) {
        setUploadProgress((prev) => ({
          ...prev,
          [file.name]: { progress: 0, status: "error" },
        }));
        showError(`Échec du téléversement de ${file.name}: ${err.message}`);
      }
    }

    const allDone = Object.values(uploadProgress).every(({ status }) => status === "completed" || status === "error");
    if (allDone) {
      setShowProgressDialog(false);
    }
    loadBucketObjects(bucketName, prefixPath);
  };

  return {
    uploadProgress,
    showProgressDialog,
    setShowProgressDialog,
    onDrop,
  };
};

export default useDragAndDrop;