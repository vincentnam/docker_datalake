import React, { Fragment, useRef } from "react";
import { Toast } from "primereact/toast";
import { useParams, useNavigate} from "react-router-dom";
import PrimaryButton from "./common/PrimaryButton";
import ListObjects from "./ListObjects/ListObjects";


const BrowseBucket = () => {
  const { bucketName, prefixPath, onDelete } = useParams();
  const childRef = useRef(null);
  const toast = useRef(null);
  const navigate = useNavigate();
  return (
    <Fragment>
      <div className="flex flex-col gap-4">
        <div className="bg-white/30 backdrop-blur-md rounded-lg shadow-lg p-6 glass-effect animate-fadeIn">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <PrimaryButton onClick={() => navigate(-1)} className="neon-button">
                <i className="pi pi-angle-left mr-2"></i> Retour
              </PrimaryButton>
              <i className="pi pi-server text-cyan-500"></i>
              <span className="text-lg font-semibold">Objects in</span>
              <span className="text-pink-800 font-bold">{bucketName}</span>
            </div>
          </div>
          <ListObjects bucketName={bucketName} path={prefixPath} ref={childRef} onDelete={onDelete} />
        </div>
      </div>
      <Toast ref={toast} />
    </Fragment>
  );
};

export default BrowseBucket;