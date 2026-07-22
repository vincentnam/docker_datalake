import React, { useState } from "react";
import { Sidebar } from "primereact/sidebar";
import PrimaryButton from "../common/PrimaryButton";
import { downloadFile } from "../../utils/fileUtils";
import usePreview from "../../hooks/usePreview";
import { getJupyterHubUrl } from "../../utils/jupyterUtils";
import "../../styles/preview.css";
import { Panel } from "primereact/panel";
import { throttle } from "lodash";

const SidebarPreview = ({ visible, onHide, selectedNode, bucketName }) => {
  const { previewComponent, isPreviewLoading, previewError } = usePreview(selectedNode, bucketName);
  const [sidebarWidth, setSidebarWidth] = useState(384);

  const throttledResize = throttle((newWidth) => {
    requestAnimationFrame(() => setSidebarWidth(newWidth));
  }, 16);

  const startResizing = (e) => {
    e.preventDefault();
    console.log("Démarrage du redimensionnement, position initiale :", e.clientX);
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
      document.removeEventListener("mousemove", doResize);
      document.removeEventListener("mouseup", stopResizing);
    };

    document.addEventListener("mousemove", doResize);
    document.addEventListener("mouseup", stopResizing);
  };
  const openJupyterHub = () => {
    // JupyterHub ouvre le serveur du user courant ou lance son authentification.
    window.location.assign(getJupyterHubUrl());
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
            <Panel
              header={selectedNode.data.name}
              className="flex-grow overflow-y-auto"
            >
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
                onClick={() =>
                  downloadFile(
                    bucketName,
                    selectedNode.key,
                    selectedNode.data.name
                  )
                }
                className="mt-4"
              >
                Télécharger
              </PrimaryButton>

              <button
                className={`bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600 transition-colors duration-300 neon-button `}
                onClick={openJupyterHub}
              >
                Ouvrir dans Jupyter Notebook
              </button>
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
    </>
  );
};

export default SidebarPreview;
