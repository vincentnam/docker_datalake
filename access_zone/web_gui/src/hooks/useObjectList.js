import { useState, useEffect } from "react";
import { orderBy } from "lodash";
import { loadObjectList, createFolder, listObjectsOfPrefix } from "../utils/objectUtils";
import prettyBytes from "pretty-bytes";

const useObjectList = (bucketName, prefixPath) => {
  const [objects, setObjects] = useState([]);
  const [loading, setLoading] = useState(false);
  const [sortOrder, setSortOrder] = useState(1); // 1 pour ascendant, -1 pour descendant
  const [sortField, setSortField] = useState("name"); // Champ de tri par défaut
  const [bucketInfo, setBucketInfo] = useState({
    creationDate: "2023-01-01",
    accessType: "Privé",
    totalSize: "0 B",
    objectCount: 0,
  });
  const [selectedNode, setSelectedNode] = useState(null);
  const [sidebarVisible, setSidebarVisible] = useState(false);

    // Fonction pour trier récursivement les nœuds
const sortNodes = (nodes, field, order) => {
  const sortedNodes = orderBy(
    nodes,
    [
      (node) => !node.leaf,
      (node) => {
        if (field === "rawSize") return node.leaf ? node.data[field] || 0 : 0;
        if (field === "lastModified") return node.data[field] ? new Date(node.data[field]).getTime() : 0;
        if (field === "uploadDate") {
          const uploadDate = node.data.metadata?.["X-Amz-Meta-Upload-Date"];
          return uploadDate ? new Date(uploadDate).getTime() || 0 : 0;
        }
        if (field === "contentType") return node.data.metadata?.["content-type"] || "";
        if (field === "etag") return node.data.etag || "";
        return (node.data[field] || "").toLowerCase();
      },
    ],
    ["desc", order === 1 ? "asc" : "desc"]
  );

  return sortedNodes.map((node) => {
    if (node.children && node.children.length > 0) {
      return { ...node, children: sortNodes(node.children, field, order) };
    }
    return node;
  });
};
  const showToast = (severity, summary, detail) => {
    console.log(`${severity}: ${summary} - ${detail}`);
  };

  const loadBucketObjects = async (bName = bucketName, pName = prefixPath) => {
    setLoading(true);
    try {
      const objList = await loadObjectList(bName, pName);
      console.log("OBJECT LIST")
      console.log(objList)
      setObjects(objList);
      const totalSize = objList.reduce((sum, node) => sum + (node.data.rawSize || 0), 0);
      const objectCount = objList.filter((node) => node.leaf).length;
      setBucketInfo((prev) => ({
        ...prev,
        totalSize: prettyBytes(totalSize),
        objectCount,
      }));
    } catch (err) {
      showToast("error", "Erreur", "Impossible de charger la liste des objets.");
    } finally {
      setLoading(false);
    }
  };

  const onExpand = async (event) => {
    const node = event.node;
    if (!node.leaf && (!node.children || node.children.length === 0)) {
      setLoading(true);
      try {
        // Utiliser data.name comme préfixe pour éviter les chemins redondants
        const folderPath = node.key.replace(/^\/+|\/+$/g, "");
        console.log(`onExpand: bucket=${bucketName}, path=${folderPath}`);

        const children = await listObjectsOfPrefix(bucketName, folderPath);
        console.log(`Enfants chargés pour ${folderPath}:`, children);

        // Mettre à jour l'arborescence
        setObjects((prev) => {
          const updatedObjects = JSON.parse(JSON.stringify(prev)); // Deep clone
          const updateNode = (nodes) => {
            for (let n of nodes) {
              if (n.key === node.key) {
                n.children = orderBy(children, ["leaf", "data.name"], ["asc", "asc"]);
                return true;
              }
              if (n.children) {
                if (updateNode(n.children)) return true;
              }
            }
            return false;
          };
          if (updateNode(updatedObjects)) {
            console.log("Arborescence mise à jour:", updatedObjects);
            return updatedObjects;
          }
          return prev;
        });
      } catch (err) {
        console.error("Erreur dans onExpand:", err);
        showToast("error", "Erreur", "Impossible de charger les fichiers du dossier.");
      } finally {
        setLoading(false);
      }
    }
  };

  const createFolderHandler = async () => {
    const folderName = prompt("Entrez le nom du dossier :");
    if (folderName) {
      try {
        await createFolder(bucketName, prefixPath, folderName);
        showToast("success", "Succès", `Dossier ${folderName} créé avec succès`);
        loadBucketObjects(bucketName, prefixPath);
      } catch (err) {
        showToast("error", "Erreur", "Impossible de créer le dossier.");
      }
    }
  };

  const refreshBucket = () => {
    loadBucketObjects(bucketName, prefixPath);
  };
  const onSort = (event) => {
    const newSortField = event.sortField === "size" ? "rawSize" : event.sortField === "uploadDate" ? "uploadDate" : event.sortField;
    const newSortOrder = event.sortOrder;
    setSortField(newSortField);
    setSortOrder(newSortOrder);
    setObjects((prev) => sortNodes(prev, newSortField, newSortOrder));
  };
  useEffect(() => {
    loadBucketObjects(bucketName, prefixPath);
  }, [bucketName, prefixPath]);

  return {
    objects,
    loading,
    bucketInfo,
    selectedNode,
    setSelectedNode,
    sidebarVisible,
    setSidebarVisible,
    loadBucketObjects,
    createFolder: createFolderHandler,
    refreshBucket,
    onExpand,
    sortOrder,
    sortField,
    setSortOrder,
    setSortField,
    onSort,
  };
};

export default useObjectList;