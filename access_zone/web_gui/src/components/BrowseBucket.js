import React, { Fragment, useRef } from "react";
import { Toast } from "primereact/toast";
import { useParams, useNavigate } from "react-router-dom";
import {
  ChevronLeft,
  Database,
  FolderOpen,
  HardDrive,
  LayoutGrid,
} from "lucide-react";
import PrimaryButton from "./common/PrimaryButton";
import ListObjects from "./ListObjects/ListObjects";

const BrowseBucket = () => {
  const { bucketName, prefixPath, onDelete } = useParams();
  const childRef = useRef(null);
  const toast = useRef(null);
  const navigate = useNavigate();

  return (
    <Fragment>
      <div className="flex flex-col gap-6 animate-fadeIn">
        {/* Header de Navigation / Breadcrumb */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-gray-200/50 pb-6">
          <div className="flex items-center gap-4">
            {/* Bouton Retour Stylisé */}
            <button
              onClick={() => navigate(-1)}
              className="group flex items-center justify-center w-10 h-10 rounded-xl bg-white/50 hover:bg-white border border-gray-200 shadow-sm transition-all duration-200 hover:scale-105 active:scale-95"
              title="Retour"
            >
              <ChevronLeft className="w-6 h-6 text-gray-600 group-hover:text-orange-600" />
            </button>

            <div className="flex flex-col">
              <div className="flex items-center gap-2 text-xs font-bold text-gray-400 uppercase tracking-widest">
                <Database size={12} className="text-orange-500" />
                Explorateur de stockage
              </div>
              <div className="flex items-center gap-2 mt-1">
                <h2 className="text-2xl font-extrabold text-gray-800 tracking-tight">
                  {bucketName}
                </h2>
                <div className="px-2 py-1 rounded-md bg-orange-100 border border-orange-200 text-orange-700 text-[10px] font-black uppercase">
                  Bucket S3
                </div>
              </div>
            </div>
          </div>

          {/*/!* Actions rapides (si tu en ajoutes plus tard) *!/*/}
          {/*<div className="flex items-center gap-3">*/}
          {/*  <div className="hidden sm:flex items-center px-4 py-2 bg-white/40 backdrop-blur-sm border border-white/60 rounded-lg text-sm text-gray-600 shadow-sm">*/}
          {/*    <FolderOpen size={16} className="mr-2 text-amber-600" />*/}
          {/*    {prefixPath ? `root / ${prefixPath}` : "Racine du bucket"}*/}
          {/*  </div>*/}
          {/*</div>*/}
        </div>

        {/* Zone de contenu principale */}
        <div className="relative overflow-hidden bg-white/40 backdrop-blur-md rounded-2xl border border-white/80 shadow-xl shadow-gray-200/50">
          {/* Un petit bandeau de statut discret au dessus de la liste */}
          <div className="flex items-center justify-between px-6 py-3 bg-gradient-to-r from-gray-50/50 to-transparent border-b border-gray-100">
            <div className="flex items-center gap-2 text-sm font-medium text-gray-500">
              <LayoutGrid size={16} />
              <span>Liste des objets</span>
            </div>
            <div className="text-xs text-gray-400">
              {new Date().toLocaleDateString()}
            </div>
          </div>

          <div className="p-2 md:p-4">
            <ListObjects
              bucketName={bucketName}
              path={prefixPath}
              ref={childRef}
              onDelete={onDelete}
            />
          </div>
        </div>
      </div>

      <Toast ref={toast} className="custom-toast" />
    </Fragment>
  );
};

export default BrowseBucket;
