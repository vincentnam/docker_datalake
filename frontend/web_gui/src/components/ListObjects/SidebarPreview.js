import React, { useState, useRef } from "react";
import { Sidebar } from "primereact/sidebar";
import { Dialog } from "primereact/dialog"; // Importer Dialog pour la popup
import PrimaryButton from "../common/PrimaryButton";
import { downloadFile } from "../../utils/fileUtils";
import usePreview from "../../hooks/usePreview";
import { checkJupyterServer, startJupyterServer, createNotebook, getNotebookUrl } from "../../utils/jupyterUtils";
import useToast from "../../hooks/useToast";
import "../../styles/preview.css";
import { Panel } from "primereact/panel";
import { throttle } from "lodash";
import { Toast } from "primereact/toast";
import { useNavigate } from "react-router-dom"; // Importer useNavigate

const SidebarPreview = ({ visible, onHide, selectedNode, bucketName }) => {
  const { previewHtml, previewComponent, isPreviewLoading, previewError } = usePreview(selectedNode, bucketName);
  const [sidebarWidth, setSidebarWidth] = useState(384);
  const [isResizing, setIsResizing] = useState(false);
  const sidebarRef = useRef(null);
  const [toast, showError, showSuccess] = useToast();
  const navigate = useNavigate();

  // États pour la popup de progression
  const [progress, setProgress] = useState(null);
  const [progressVisible, setProgressVisible] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  const throttledResize = throttle((newWidth) => {
    requestAnimationFrame(() => setSidebarWidth(newWidth));
  }, 16);

  const startResizing = (e) => {
    e.preventDefault();
    console.log("Démarrage du redimensionnement, position initiale :", e.clientX);
    setIsResizing(true);
    const startX = e.clientX;
    const startWidth = sidebarWidth;

    const doResize = (e) => {
      const newWidth = startWidth + (startX - e.clientX);
      const minWidth = 200;
      const maxWidth = window.innerWidth * 0.8;
      const clampedWidth = Math.min(Math.max(newWidth, minWidth), maxWidth);
      console.log("Nouvelle largeur calculée :", clampedWidth);
      throttledResize(clampedWidth);
    };

    const stopResizing = () => {
      console.log("Arrêt du redimensionnement");
      setIsResizing(false);
      document.removeEventListener("mousemove", doResize);
      document.removeEventListener("mouseup", stopResizing);
    };

    document.addEventListener("mousemove", doResize);
    document.addEventListener("mouseup", stopResizing);
  };
  // Messages de progression
  const progressMessages = {
    checking_server: "Vérification du serveur Jupyter...",
    starting_server: "Lancement du serveur Jupyter...",
    creating_notebook: "Création du notebook...",
    redirecting: "Redirection vers le notebook...",
    error: "Une erreur est survenue.",
  };

  // Fonction pour générer le contenu du notebook
  const generateNotebookContent = (dataInfo) => {
    /*Pas la bonne image, nécessaire pour enlever "!pip install minio"*/
    const code = [
      "!pip install minio \n",
      "# Code pour télécharger les données depuis MinIO\n",
      `bucket_name = "${dataInfo.bucketName}"\n`,
      `object_key = "${dataInfo.key}"\n`,
      "from minio import Minio\n",
      'client = Minio("raw_data_storage:9000", access_key="admin", secret_key="adminadmin", secure=False)\n',
      "client.fget_object(bucket_name, object_key, 'downloaded_file')\n",
      "# Le fichier est maintenant téléchargé localement sous 'downloaded_file'\n",
    ];

    return {
      cells: [
        {
          cell_type: "code",
          execution_count: null,
          metadata: {},
          outputs: [],
          source: code,
        },
      ],
      metadata: {
        kernelspec: {
          display_name: "Python 3",
          language: "python",
          name: "python3",
        },
        language_info: {
          codemirror_mode: { name: "ipython", version: 3 },
          file_extension: ".py",
          mimetype: "text/x-python",
          name: "python",
          nbconvert_exporter: "python",
          pygments_lexer: "ipython3",
          version: "3.8.5",
        },
      },
      nbformat: 4,
      nbformat_minor: 4,
    };
  };

  // Fonction pour ouvrir le notebook
  const openInJupyter = async () => {
    if (!selectedNode || !selectedNode.leaf) {
      showError("Erreur", "Veuillez sélectionner un fichier");
      return;
    }

    setProgressVisible(true);
    setProgress("checking_server");

    try {
      const username = "admin"; // Remplacer par l'utilisateur actuel si nécessaire
      const serverRunning = await checkJupyterServer(username);

      if (!serverRunning) {
        setProgress("starting_server");
        await startJupyterServer(username);
        // Attendre 5 secondes pour s'assurer que le serveur est prêt
        await new Promise((resolve) => setTimeout(resolve, 5000));
      }

      setProgress("creating_notebook");
      const notebookName = `notebook-${Date.now()}`;
      const content = generateNotebookContent({ bucketName, key: selectedNode.key });
      await createNotebook(username, notebookName, content);

      setProgress("redirecting");
      const notebookUrl = getNotebookUrl(username, notebookName);
      navigate(notebookUrl.replace("http://localhost:8000", "")); // Redirection dans l'historique
      window.location.href = notebookUrl; // Forcer la navigation pour ouvrir dans le même onglet
    } catch (err) {
      setProgress("error");
      setErrorMessage(err.message);
      showError("Erreur", err.message);
    }
  };

  return (
    <>
<Sidebar
  visible={visible}
  onHide={onHide}
  position="right"
  className="ui-sidebar-lg sidebar-preview"
  style={{ width: `${sidebarWidth}px`, position: "relative" }}
  baseZIndex={1000}
>
  <div className="resize-handle" onMouseDown={startResizing}></div>
        <div className="flex flex-col h-full">
          <div className="resize-handle" onMouseDown={startResizing}></div>
          {selectedNode && (
            <Panel header={selectedNode.data.name} className="flex-grow overflow-y-auto">
              <p>Taille : {selectedNode.data.size || "-"}</p>
              <p>Type : {selectedNode.data["contentType"] || "-"}</p>
              <p>
                Dernière modification :{" "}
                {selectedNode.data.lastModified
                  ? new Date(selectedNode.data.lastModified).toLocaleString()
                  : "-"}
              </p>
              <p>
                Date de téléversement :{" "}
                {selectedNode.data.creationDate
                  ? new Date(selectedNode.data.creationDate).toLocaleString()
                  : "-"}
              </p>
              <PrimaryButton
                onClick={() => downloadFile(bucketName, selectedNode.key, selectedNode.data.name)}
                className="mt-4"
              >
                Télécharger
              </PrimaryButton>
              <PrimaryButton onClick={openInJupyter} className="mt-4 ml-2">
                Ouvrir dans Jupyter Notebook
              </PrimaryButton>
              {isPreviewLoading ? (
                <p>Chargement de la prévisualisation...</p>
              ) : previewError ? (
                <p>{previewError}</p>
              ) : (
                previewComponent
              )}
            </Panel>
          )}
        </div>
      </Sidebar>
      <Dialog
        header="Progression"
        visible={progressVisible}
        onHide={() => setProgressVisible(false)}
        style={{ width: "50vw" }}
      >
        <p>{progressMessages[progress]}</p>
        {progress === "error" && <p>{errorMessage}</p>}
      </Dialog>
      <Toast ref={toast} />
    </>
  );
};

export default SidebarPreview;