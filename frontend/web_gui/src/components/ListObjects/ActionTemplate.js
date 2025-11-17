import React from "react";
import { downloadFile } from "../../utils/fileUtils";
import { useNavigate } from "react-router-dom";

const ActionTemplate = ({ node, onDelete, bucketName }) => {
  const fileType = node.data.metadata?.["content-type"] || "";
  const navigate = useNavigate();
  return (
    <div className="flex gap-2">
      <button
        type="button"
        className="bg-white hover:bg-gray-200 flex items-center p-1 rounded"
        onClick={() => onDelete?.({ node })}
        disabled={!node.leaf}
      >
        <i className="pi pi-trash"></i>
      </button>
      {!node.leaf && (
        <button
          type="button"
          className="bg-white hover:bg-gray-200 flex items-center p-1 rounded"
          onClick={() => navigate(`/buckets/${bucketName}?path=${node.key}`)}
        >
          <i className="pi pi-window-maximize"></i>
        </button>
      )}
      {node.leaf && fileType && (
        <button
          type="button"
          className="bg-white hover:bg-gray-200 flex items-center p-1 rounded"
          onClick={() => downloadFile(bucketName, node.key, node.data.name)}
        >
          <i className="pi pi-download"></i>
        </button>
      )}
    </div>
  );
};

export default ActionTemplate;