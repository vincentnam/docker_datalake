// src/Layout/Header.js
import React, { useState, useEffect, useMemo } from "react";
// Ajout de Database dans les imports lucide-react
import { Link, useLocation, useNavigate } from "react-router-dom";
import { LogOut, Server, Menu, X, ChevronDown, Database } from "lucide-react";
import {
  getAuthData,
  getActiveProject,
  getAvailableProjects,
  getSessionCredentials,
  setAuthData,
  setActiveProject,
  clearAuthData,
} from "../utils/authUtils";
import { loginWithCredentials, logout, getSsoLogoutUrl } from "../utils/apiClient";

const Header = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isSwitchingProject, setIsSwitchingProject] = useState(false);
  const [activeProject, setActiveProjectState] = useState(getActiveProject());

  const location = useLocation();
  const navigate = useNavigate();

  const authData = getAuthData();
  const isAuthenticated = Boolean(
    authData?.status === "authenticated" && authData?.access_token
  );
  const projects = useMemo(
    () => getAvailableProjects(),
    [authData?.access_token]
  );

  useEffect(() => {
    setActiveProjectState(getActiveProject());
  }, [location.pathname]);

  const handleProjectChange = async (e) => {
    const nextProject = e.target.value;
    if (!nextProject || nextProject === activeProject) return;

    const credentials = getSessionCredentials();
    if (!credentials?.username || !credentials?.password) {
      clearAuthData();
      navigate("/");
      return;
    }

    setIsSwitchingProject(true);
    try {
      const refreshedAuthData = await loginWithCredentials({
        username: credentials.username,
        password: credentials.password,
        project: nextProject,
      });

      setAuthData(refreshedAuthData);
      setActiveProject(nextProject);
      setActiveProjectState(nextProject);

      window.dispatchEvent(new Event("projectChanged"));
      // Redirection automatique vers les buckets lors du changement de projet
      navigate("/buckets");
    } catch (error) {
      console.error("Erreur changement:", error);
    } finally {
      setIsSwitchingProject(false);
    }
  };

  return (
    <header className="sticky top-0 z-50 bg-gradient-to-r from-amber-600 via-orange-600 to-amber-700 border-b border-white/10 shadow-xl">
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-3 group">
          <div className="w-9 h-9 bg-white/20 backdrop-blur-md rounded-xl flex items-center justify-center border border-white/30 transition-transform group-hover:scale-105">
            <Server className="w-5 h-5 text-white" />
          </div>
          <span className="text-xl font-bold tracking-tight text-white uppercase italic">
            Lac de Données
          </span>
        </Link>

        <nav className="hidden md:flex items-center gap-6">
          {isAuthenticated && (
            <>
              {/* --- NOUVEAU BOUTON RETOUR BUCKETS --- */}
              <Link
                to="/buckets"
                className="flex items-center gap-2 px-3 py-2 bg-white/10 hover:bg-white/20 rounded-xl text-white text-sm font-semibold transition-all border border-white/10"
              >
                <Database size={16} />
                <span>Accueil</span>
              </Link>
              <div className="h-6 w-[1px] bg-white/20 mx-1" />{" "}
              {/* Séparateur visuel */}
              {/* Sélecteur de Projet */}
              <div className="relative flex items-center gap-2">
                <span className="text-[10px] font-black text-white/60 uppercase tracking-widest">
                  Projet
                </span>
                <div className="relative">
                  <select
                    value={activeProject}
                    onChange={handleProjectChange}
                    disabled={isSwitchingProject}
                    className="bg-white/10 hover:bg-white/20 backdrop-blur-md text-white text-sm font-bold px-4 py-2 rounded-xl border border-white/20 outline-none appearance-none pr-10 transition-all cursor-pointer disabled:opacity-50"
                  >
                    {projects.map((p) => (
                      <option
                        key={p.name}
                        value={p.name}
                        className="text-gray-900"
                      >
                        {p.name}
                      </option>
                    ))}
                  </select>
                  <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/70 pointer-events-none" />
                </div>
              </div>
              <button
                onClick={async () => {
                  // Revoke the Keystone token server-side, clear local state,
                  // then leave through a full-page navigation so Keycloak can
                  // clear its SSO cookie too — otherwise "Se connecter avec
                  // Keycloak" silently re-logs the same account.
                  await logout();
                  clearAuthData();
                  window.location.href = getSsoLogoutUrl();
                }}
                className="flex items-center gap-2 px-4 py-2 bg-black/20 hover:bg-black/40 rounded-xl text-white text-sm font-medium transition-all border border-white/5"
              >
                <LogOut size={16} />
                Se déconnecter
              </button>
            </>
          )}
        </nav>
      </div>
    </header>
  );
};

export default Header;
