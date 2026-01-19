import React from "react";
import { Dialog } from "primereact/dialog";
import { ProgressBar } from "primereact/progressbar";

const UploadProgressDialog = ({ visible, onHide, uploadProgress }) => {
  return (
    <Dialog
      header="Progression du téléversement"
      visible={visible}
      style={{ width: "30vw", position: "fixed", right: 0, top: 0 }}
      onHide={onHide}
      draggable={false}
      resizable={false}
    >
      <div className="p-4">
        {Object.keys(uploadProgress).length > 0 ? (
          Object.entries(uploadProgress).map(([fileName, { progress, status }]) => (
            <div key={fileName} className="mb-4">
              <div className="flex justify-between mb-1">
                <span>{fileName}</span>
                <span>
                  {status === "completed" ? "Terminé" : status === "error" ? "Erreur" : `${progress}%`}
                </span>
              </div>
              <ProgressBar value={progress} style={{ height: "20px" }} />
            </div>
          ))
        ) : (
          <p>Aucun téléversement en cours.</p>
        )}
      </div>
    </Dialog>
  );
};

export default UploadProgressDialog;