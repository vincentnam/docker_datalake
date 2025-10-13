import React, { forwardRef, useRef, useImperativeHandle } from "react";
import { TreeTable } from "primereact/treetable";
import { Column } from "primereact/column";
import { Toast } from "primereact/toast";
import { DndProvider } from "react-dnd";
import { HTML5Backend } from "react-dnd-html5-backend";
import { useLocation, useParams } from "react-router-dom";
import { useDropzone } from "react-dropzone";
import FileRow from "./FileRow";
import FolderRow from "./FolderRow";
import ActionTemplate from "./ActionTemplate";
import SidebarPreview from "./SidebarPreview";
import UploadProgressDialog from "./UploadProgressDialog";
import useObjectList from "../../hooks/useObjectList";
import useDragAndDrop from "../../hooks/useDragAndDrop";
import history from "../../history";

const ListObjects = forwardRef(({ bucketName, path: initialPath, onDelete }, ref) => {
  const { search } = useLocation();
  const params = new URLSearchParams(search);
  const prefixPath = params.get("path") || initialPath || "";
  const toast = useRef(null);

  /*const {
    objects,
    loading,
    bucketInfo,
    selectedNode,
    setSelectedNode,
    sidebarVisible,
    setSidebarVisible,
    loadBucketObjects,
    createFolder,
    refreshBucket,
    onExpand,
    sortOrder,
    setSortOrder,
  } = useObjectList(bucketName, prefixPath);
*/
  const {
    objects,
    loading,
    bucketInfo,
    selectedNode,
    setSelectedNode,
    sidebarVisible,
    setSidebarVisible,
    loadBucketObjects,
    createFolder,
    refreshBucket,
    onExpand,
    sortOrder,
    sortField,
    setSortOrder,
    setSortField,
    onSort,
  } = useObjectList(bucketName, prefixPath);


  const { uploadProgress, showProgressDialog, setShowProgressDialog, onDrop } = useDragAndDrop(
    bucketName,
    prefixPath,
    loadBucketObjects,
    toast
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop, noClick: true });

  useImperativeHandle(ref, () => ({
    refresh(b = bucketName, p = prefixPath) {
      loadBucketObjects(b, p);
    },
    refreshChildren(evt) {
      onExpand(evt);
    },
  }));


  const rowClassName = (node) => ({
    "p-highlight": false,
    "object-tree-row": true,
  });

  return (
    <DndProvider backend={HTML5Backend}>
      <Toast ref={toast} />
      <div className="flex flex-col h-full">
        <div className="bg-gray-100 p-4 border-b flex justify-between items-center">
          <div>
            <p>Date de création : {bucketInfo.creationDate}</p>
            <p>Type d'accès : {bucketInfo.accessType}</p>
            <p>Taille totale : {bucketInfo.totalSize}</p>
            <p>Nombre d'objets : {bucketInfo.objectCount}</p>
          </div>
          <div className="flex gap-2">
            <button
              type="button"
              className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
              onClick={createFolder}
            >
              Créer un dossier
            </button>
            <button
              type="button"
              className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600"
              onClick={refreshBucket}
            >
              Rafraîchir
            </button>
          </div>
        </div>
        <div {...getRootProps()} className="relative flex-grow overflow-auto">
          <input {...getInputProps()} />
          {isDragActive && (
            <div className="absolute inset-0 flex items-center justify-center bg-gray-200 bg-opacity-50 z-10">
              <p className="text-lg font-semibold">Déposez les fichiers ici...</p>
            </div>
          )}
          <div className="flex-grow overflow-auto min-w-min overflow-x-auto">
            <TreeTable
                tableStyle={{ minWidth: '100%' }}
                className="object-tree-table"
                value={objects}
                lazy
                onExpand={onExpand}
                loading={loading}

                style={{width: "100%"}}
                rowClassName={rowClassName}

                sortMode="single"
                sortField={sortField}
                sortOrder={sortOrder}
                onSort={onSort}
                reorderableColumns
                resizableColumns
                columnResizeMode={"expand"}
            >
              <Column
                  field="name"
                  header="Nom"
                  expander
                  sortable
                  sortField="name"
                  body={(node) =>

                      node.leaf ? <FileRow node={node} setSelectedNode={setSelectedNode}
                                           setSidebarVisible={setSidebarVisible}/> :
                          <FolderRow node={node} bucketName={bucketName}/>
                  }
                  className="whitespace-nowrap overflow-hidden text-overflow-ellipsis flex-grow"
              />
              <Column
                  field="rawSize"
                  header="Taille"
                  sortable
                  sortField="rawSize"
                  body={(node) => node.data.size || "-"}
                  className="whitespace-nowrap overflow-hidden text-overflow-ellipsis flex-grow"
              />
              <Column
                  field="uploadDate"
                  header="Date de téléversement"
                  body={(node) => {

                    const uploadDate = node.data.metadata?.["X-Amz-Meta-Upload-Date"] || "";
                    return uploadDate ? new Date(uploadDate).toLocaleString() : "-";
                  }}
                  sortable
                  sortField="uploadDate"
                  className="whitespace-nowrap overflow-hidden text-overflow-ellipsis flex-grow"
              />
              <Column
                  field="lastModified"
                  header="Dernière modification"
                  body={(node) => (node.data.lastModified ? new Date(node.data.lastModified).toLocaleString() : "-")}
                  sortable
                  sortField="lastModified"
                  className="whitespace-nowrap overflow-hidden text-overflow-ellipsis flex-grow"
              />
              <Column
                  field="contentType"
                  header="Type de contenu"
                  body={(node) => node.data.metadata?.["content-type"] || "-"}
                  sortable
                  sortField="contentType"
                  className="whitespace-nowrap overflow-hidden text-overflow-ellipsis flex-grow"
              />
              <Column
                  field="etag"
                  header="Clé de stockage"
                  body={(node) => node.data.etag || "-"}
                  sortable
                  sortField="etag"
                  className="whitespace-nowrap overflow-hidden text-overflow-ellipsis flex-grow"
              />


              <Column
                  field="actions"
                  header="Actions"
                  body={(node) => <ActionTemplate node={node} onDelete={onDelete} bucketName={bucketName}/>}
                  alignHeader={"center"}
                  className="whitespace-nowrap overflow-hidden text-overflow-ellipsis flex-grow"
              />

            </TreeTable>
            <div

                className="bg-gray-100 border-t border-gray-300 flex items-center justify-center cursor-pointer sticky bottom-0 z-10 h-16 "
                onClick={() => document.querySelector('input[type="file"]').click()}
            >
              <p className="text-sm font-semibold">Glissez-déposez vos fichiers ici ou cliquez pour sélectionner</p>
            </div>
          </div>

        </div>
      </div>
      <SidebarPreview
          visible={sidebarVisible}
          onHide={() => setSidebarVisible(false)}
          selectedNode={selectedNode}
          bucketName={bucketName}
      />
      <UploadProgressDialog
          visible={showProgressDialog}
          onHide={() => setShowProgressDialog(false)}
          uploadProgress={uploadProgress}
      />
    </DndProvider>
  );
});

export default ListObjects;