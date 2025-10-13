import { useState } from "react";
import fileReaderStream from "filereader-stream";
import mc from "../utils/mc";

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
        const readStream = fileReaderStream(file);
        const filePath = `${prefixPath ? prefixPath.replace(/\/+$/, "") + "/" : ""}${file.name}`.replace(/\/+/g, "/");
        const uploadDate = new Date().toISOString();

        let progress = 0;
        const interval = setInterval(() => {
          progress += 10;
          setUploadProgress((prev) => ({
            ...prev,
            [file.name]: { ...prev[file.name], progress },
          }));
          if (progress >= 100) clearInterval(interval);
        }, 500);

        await mc.putObject(bucketName, filePath, readStream, {
          "Content-Type": file.type || "application/octet-stream",
          "X-Amz-Meta-App": "SPH-REACT-JS",
          "X-Amz-Meta-Upload-Date": uploadDate,
        });

        clearInterval(interval);
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
        showError(`Échec du téléversement de ${file.name}`);
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