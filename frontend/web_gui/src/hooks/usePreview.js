// src/hooks/usePreview.js
import { useState, useEffect } from "react";
import { getPreviewContent } from "../utils/previewUtils";

const usePreview = (selectedNode, bucketName) => {
  const [previewHtml, setPreviewHtml] = useState("");
  const [previewComponent, setPreviewComponent] = useState(null);
  const [previewError, setPreviewError] = useState(null);
  const [isPreviewLoading, setIsPreviewLoading] = useState(false);

  useEffect(() => {
    if (selectedNode) {
      setIsPreviewLoading(true);
      getPreviewContent(bucketName, selectedNode).then(({ component, error }) => {
        setPreviewComponent(component);
        setPreviewHtml(""); // Garder pour compatibilité si nécessaire
        setPreviewError(error);
        setIsPreviewLoading(false);
      });
    } else {
      setPreviewHtml("");
      setPreviewComponent(null);
      setPreviewError(null);
    }
  }, [selectedNode, bucketName]);

  return { previewHtml, previewComponent, previewError, isPreviewLoading };
};

export default usePreview;