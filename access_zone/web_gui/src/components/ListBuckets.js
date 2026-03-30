// src/components/ListBuckets.js
import React, { useEffect, useState, useCallback, useMemo } from "react";
import { getBuckets, removeBucket } from "../utils/s3client";
import { getActiveProject, getAuthData } from "../utils/authUtils";
import { DataTable } from "primereact/datatable";
import { Column } from "primereact/column";
import NewBucket from "./NewBucket/NewBucket";
import ProjectAdministration from "./ProjectAdministration";
import { Toast } from "primereact/toast";
import useToast from "../hooks/useToast";
import {
  Trash2,
  Folder,
  Database,
  LayoutGrid,
  Cpu,
  Globe,
  Calendar,
  ExternalLink,
  ShieldCheck,
} from "lucide-react";

const ListBuckets = () => {
  const [buckets, setBuckets] = useState([]);
  const [loading, setLoading] = useState(false);
  const [toast, showError, showSuccess] = useToast();
  // Extraction des rôles depuis l'authData
  // --- CHANGEMENT ICI : On utilise un état pour les infos du projet ---
  const [projectData, setProjectData] = useState({
    name: getActiveProject(),
    roles: getAuthData()?.user?.roles || [],
  });
  const fetchBuckets = useCallback(async () => {
    setLoading(true);
    try {
      const activeProj = getActiveProject();
      const auth = getAuthData();

      // Mise à jour synchronisée des infos du projet et des rôles
      setProjectData({
        name: activeProj,
        roles: auth?.user?.roles || [],
      });

      const data = await getBuckets(activeProj);
      setBuckets(Array.isArray(data) ? data : []);
    } catch (err) {
      // On évite d'afficher l'erreur en boucle si l'API échoue
      console.error("Erreur fetch:", err);
    } finally {
      setLoading(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Dépendances vides : la fonction est créée une seule fois

  useEffect(() => {
    fetchBuckets();
    window.addEventListener("projectChanged", fetchBuckets);
    return () => window.removeEventListener("projectChanged", fetchBuckets);
  }, [fetchBuckets]);

  const handleRemove = async (name) => {
    if (!window.confirm(`Supprimer ${name} ?`)) return;
    try {
      await removeBucket(name, projectData.name);
      showSuccess("Bucket supprimé");
      fetchBuckets();
    } catch (err) {
      showError(err.message);
    }
  };

  // --- Templates ---
  const tableHeader = () => (
    <div className="flex justify-between items-center p-4">
      <div className="flex items-center gap-3">
        <div className="p-2 bg-amber-50 rounded-lg">
          <Database className="w-5 h-5 text-amber-600" />
        </div>
        <h2 className="text-xl font-bold text-gray-800 tracking-tight">
          Espaces de stockage
        </h2>
      </div>
      <NewBucket onRefresh={fetchBuckets} />
    </div>
  );

  return (
    <div className="min-h-screen bg-[#F8F9FB] pb-20">
      <Toast ref={toast} />

      <div className="bg-white border-b border-gray-200 px-8 py-10 mb-8 shadow-sm">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
            <div>
              <div className="flex items-center gap-2 mb-2">
                <LayoutGrid size={18} className="text-amber-600" />
                <span className="text-[10px] font-black uppercase tracking-[0.2em] text-amber-600">
                  Vue d'ensemble
                </span>
              </div>
              <h1 className="text-4xl font-black text-gray-900 tracking-tighter uppercase italic">
                Projet :{" "}
                <span className="text-amber-600">{projectData.name}</span>
              </h1>
            </div>

            {/* Affichage des Rôles */}
            <div className="flex flex-wrap gap-2 max-w-md md:justify-end">
              <div className="flex items-center gap-2 w-full md:justify-end mb-1">
                <ShieldCheck size={14} className="text-green-600" />
                <span className="text-[10px] font-bold text-gray-400 uppercase tracking-widest">
                  Vos habilitations :
                </span>
              </div>
              {projectData.roles.map((role, index) => (
                <span
                  key={index}
                  className="px-2.5 py-1 bg-green-50 text-green-700 text-[10px] font-bold rounded-md border border-green-100 uppercase"
                >
                  {role}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-6 space-y-10">
        {/* 1. SECTION STORAGE */}
        <div className="bg-white rounded-[2rem] border border-gray-100 shadow-xl shadow-gray-200/40 overflow-hidden">
          <DataTable
            value={buckets}
            header={tableHeader}
            loading={loading}
            className="p-datatable-sm"
            emptyMessage="Aucun bucket trouvé dans ce projet."
          >
            <Column
              header="NOM DU BUCKET"
              body={(rowData) => (
                <div className="flex items-center gap-3 py-2">
                  <Folder className="w-4 h-4 text-amber-500" />
                  <span className="font-bold text-gray-700 tracking-tight">
                    <a className="text-pink-700 underline hover:text-blue-800" href={`/buckets/${rowData.Name}`} rel="noopener noreferrer">{rowData.Name}</a>
                  </span>

                  <ExternalLink
                    size={12}
                    className="text-gray-300 opacity-0 group-hover:opacity-100"
                  />
                </div>
              )}
            />
            <Column
              header="DATE DE CRÉATION"
              body={(r) => (
                <div className="flex items-center gap-2 text-gray-400 text-xs font-medium">
                  <Calendar size={14} />
                  {new Date(r.CreationDate).toLocaleDateString()}
                </div>
              )}
            />
            <Column
              style={{ width: "80px" }}
              body={(r) => (
                <button
                  onClick={() => handleRemove(r.Name)}
                  className="p-2 text-gray-300 hover:text-red-500 hover:bg-red-50 rounded-xl transition-all"
                >
                  <Trash2 size={18} />
                </button>
              )}
            />
          </DataTable>
        </div>

        <ProjectAdministration
          projectName={projectData.name}
          showSuccess={showSuccess}
          showError={showError}
        />

        {/* 2. SECTION CALCUL & APPS (Placeholders) */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Calcul */}
          <div className="p-10 bg-white rounded-[2rem] border border-gray-100 shadow-lg flex flex-col items-center text-center group hover:border-blue-200 transition-all">
            <div className="p-4 bg-blue-50 rounded-2xl mb-4 group-hover:scale-110 transition-transform">
              <Cpu className="w-8 h-8 text-blue-500" />
            </div>
            <h3 className="text-lg font-black text-gray-800 uppercase tracking-tight">
              Environnements de calcul
            </h3>
            <p className="text-sm text-gray-400 mt-2 font-medium">
              JupyterHub, Spark & Clusters GPU
            </p>
            <span className="mt-4 px-3 py-1 bg-gray-100 text-[10px] font-black text-gray-400 rounded-full uppercase tracking-widest">
              Bientôt disponible
            </span>
          </div>

          {/* Apps */}
          <div className="p-10 bg-white rounded-[2rem] border border-gray-100 shadow-lg flex flex-col items-center text-center group hover:border-purple-200 transition-all">
            <div className="p-4 bg-purple-50 rounded-2xl mb-4 group-hover:scale-110 transition-transform">
              <Globe className="w-8 h-8 text-purple-500" />
            </div>
            <h3 className="text-lg font-black text-gray-800 uppercase tracking-tight">
              Applications Web
            </h3>
            <p className="text-sm text-gray-400 mt-2 font-medium">
              Déploiement Shiny, Streamlit & Dash
            </p>
            <span className="mt-4 px-3 py-1 bg-gray-100 text-[10px] font-black text-gray-400 rounded-full uppercase tracking-widest">
              Bientôt disponible
            </span>
          </div>
        </div>
      </div>

      <style>{`
        .p-datatable-header { background: white !important; border-bottom: 1px solid #f3f4f6 !important; }
        .p-datatable-thead > tr > th { 
          background: #fafafa !important; 
          color: #9ca3af !important; 
          font-size: 10px !important; 
          font-weight: 900 !important; 
          letter-spacing: 0.1em !important;
          padding: 1.5rem 1rem !important;
        }
        .p-datatable-tbody > tr { border-bottom: 1px solid #f9fafb !important; }
      `}</style>
    </div>
  );
};

export default ListBuckets;
