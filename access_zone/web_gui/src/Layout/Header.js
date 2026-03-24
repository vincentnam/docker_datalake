// src/Layout/Header.js
import React, { useState, useEffect, useMemo } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { LogOut, Server, Menu, X, ChevronDown } from "lucide-react";
import {
  getAuthData,
  getActiveProject,
  getAvailableProjects,
  getSessionCredentials,
  setAuthData,
  setActiveProject,
  clearAuthData,
} from "../utils/authUtils";
import { loginWithCredentials } from "../utils/apiClient";

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

      // On prévient le composant ListBuckets du changement
      window.dispatchEvent(new Event("projectChanged"));
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
          <div className="w-9 h-9 bg-white/20 backdrop-blur-md rounded-xl flex items-center justify-center border border-white/30">
            <Server className="w-5 h-5 text-white" />
          </div>
          <span className="text-xl font-bold tracking-tight text-white uppercase italic">
            Lac de Données
          </span>
        </Link>

        <nav className="hidden md:flex items-center gap-6">
          {isAuthenticated && (
            <>
              {/* Sélecteur de Projet */}
              <div className="relative flex items-center gap-2">
                <span className="text-[10px] font-black text-white/60 uppercase tracking-widest">
                  Projet
                </span>
                <select
                  value={activeProject}
                  onChange={handleProjectChange}
                  disabled={isSwitchingProject}
                  className="bg-white/10 hover:bg-white/20 backdrop-blur-md text-white text-sm font-bold px-4 py-2 rounded-xl border border-white/20 outline-none appearance-none pr-10 transition-all cursor-pointer"
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

              <button
                onClick={() => {
                  clearAuthData();
                  navigate("/");
                }}
                className="flex items-center gap-2 px-4 py-2 bg-black/10 hover:bg-black/20 rounded-xl text-white text-sm font-medium transition-all"
              >
                <LogOut size={16} />
                Quitter
              </button>
            </>
          )}
        </nav>
      </div>
    </header>
  );
};

export default Header;
