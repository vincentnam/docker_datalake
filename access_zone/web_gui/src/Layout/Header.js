import React, { useEffect, useMemo, useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import {
  clearAuthData,
  getActiveProject,
  getAuthData,
  getAvailableProjects,
  getSessionCredentials,
  setActiveProject,
  setAuthData,
} from '../utils/authUtils';
import { loginWithCredentials } from '../utils/apiClient';

const Header = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isSwitchingProject, setIsSwitchingProject] = useState(false);
  const [activeProject, setActiveProjectState] = useState(getActiveProject());
  const location = useLocation();
  const navigate = useNavigate();

  const authData = getAuthData();
  const isAuthenticated = Boolean(authData?.status === 'authenticated' && authData?.access_token);
  const projects = useMemo(() => getAvailableProjects(), [authData?.access_token]);

  useEffect(() => {
    setActiveProjectState(getActiveProject());
  }, [authData?.access_token, location.pathname]);

  const toggleMenu = () => setIsMenuOpen((prev) => !prev);

  const handleProjectChange = async (event) => {
    const nextProject = event.target.value;
    if (!nextProject || nextProject === activeProject) {
      return;
    }

    const credentials = getSessionCredentials();
    if (!credentials?.username || !credentials?.password) {
      clearAuthData();
      navigate('/');
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
      navigate('/buckets');
    } catch (error) {
      console.error('Erreur changement de projet:', error);
      setActiveProjectState(activeProject);
    } finally {
      setIsSwitchingProject(false);
    }
  };

  const handleLogout = () => {
    clearAuthData();
    navigate('/');
  };

  return (
    <header className="w-full h-16 bg-amber-600 rounded-md bg-clip-padding backdrop-filter backdrop-blur-lg bg-opacity-70 border border-gray-100 drop-shadow-lg sticky top-0 z-50">
      <div className="container px-4 md:px-0 h-full mx-auto flex justify-between items-center">
        <Link to={isAuthenticated ? '/buckets' : '/'} className="flex items-center space-x-2 group">
          <span className="text-xl font-bold hover:scale-110 group-hover:text-red-100 transition-colors duration-300">
            Lac de donnees
          </span>
        </Link>

        <button
          className="md:hidden focus:outline-none neon-button"
          onClick={toggleMenu}
          aria-label="Toggle menu"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              d={isMenuOpen ? 'M6 18L18 6M6 6l12 12' : 'M4 6h16M4 12h16M4 18h16'}
            />
          </svg>
        </button>

        <nav
          className={`${
            isMenuOpen ? 'flex' : 'hidden'
          } md:flex flex-col md:flex-row absolute md:static top-16 left-0 w-full md:w-auto bg-pink-700/90 md:bg-transparent p-4 md:p-0 space-y-4 md:space-y-0 md:space-x-6 animate-slideInRight glass-effect`}
        >
          {isAuthenticated && (
            <>
              <div className="flex items-center gap-2">
                <label htmlFor="project-select" className="text-sm text-white md:text-inherit">
                  Projet
                </label>
                <select
                  id="project-select"
                  className="rounded px-2 py-1 text-sm text-black"
                  value={activeProject}
                  onChange={handleProjectChange}
                  disabled={isSwitchingProject}
                >
                  {projects.length > 0 ? (
                    projects.map((project) => (
                      <option key={project.id || project.name} value={project.name}>
                        {project.name}
                      </option>
                    ))
                  ) : (
                    <option value={activeProject}>{activeProject}</option>
                  )}
                </select>
              </div>

              <Link
                to="/buckets"
                className="opacity-70 hover:scale-110 hover:text-red-100 hover:opacity-100 transition-all duration-300"
                onClick={() => setIsMenuOpen(false)}
              >
                Vos donnees (Buckets)
              </Link>

              <button
                type="button"
                className="opacity-70 hover:scale-110 hover:text-red-100 hover:opacity-100 transition-all duration-300 text-left"
                onClick={handleLogout}
              >
                Deconnexion
              </button>
            </>
          )}
        </nav>
      </div>
    </header>
  );
};

export default Header;
