import React, { useState, useEffect } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import { User, Lock, ArrowRight, Loader2, AlertCircle, KeyRound } from "lucide-react";
import {
  getAuthData,
  setActiveProject,
  setAuthData,
  setSessionCredentials,
} from "../utils/authUtils";
import {
  loginWithCredentials,
  loginWithToken,
  getSsoLoginUrl,
  fetchAuthConfig,
} from "../utils/apiClient";

const Login = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  // Identity providers registered in Keystone : one login button per entry.
  const [idps, setIdps] = useState([]);
  const [showClassic, setShowClassic] = useState(false);
  const ssoEnabled = idps.length > 0;
  const navigate = useNavigate();

  // On mount : finalize an SSO return, OR skip login if already authenticated.
  useEffect(() => {
    const params = new URLSearchParams(window.location.hash.slice(1));
    const ssoToken = params.get("sso_token");
    const ssoError = params.get("sso_error");
    const ssoProject = params.get("project");
    const ssoProjectId = params.get("project_id");

    const clearHash = () =>
      window.history.replaceState(null, "", window.location.pathname);

    if (ssoError) {
      setError(ssoError);
      clearHash();
      return;
    }

    if (ssoToken) {
      // Came back from Keycloak SSO : exchange the Keystone token for the full
      // auth payload, store it, then go to the app.
      setLoading(true);
      loginWithToken({ token: ssoToken, project: ssoProject, projectId: ssoProjectId })
        .then((data) => {
          setAuthData(data);
          if (ssoProject) {
            setActiveProject(ssoProject);
          }
          clearHash();
          navigate("/buckets");
        })
        .catch((err) => {
          setError(err.message || "Echec de connexion SSO");
          clearHash();
          setLoading(false);
        });
      return;
    }

    // Ask the API for the login options (identity providers list).
    fetchAuthConfig().then((cfg) =>
      setIdps(cfg.sso_enabled ? cfg.idps : [])
    );
  }, [navigate]);

  // A valid token is already stored and we're not finalizing an SSO return :
  // never render the login page, the app's default page is the buckets.
  const hashParams = new URLSearchParams(window.location.hash.slice(1));
  const isSsoReturn = hashParams.has("sso_token") || hashParams.has("sso_error");
  const storedAuth = getAuthData();
  if (
    !isSsoReturn &&
    storedAuth?.status === "authenticated" &&
    storedAuth?.access_token
  ) {
    return <Navigate to="/buckets" replace />;
  }

  const handleSsoLogin = (idpId) => {
    window.location.href = getSsoLoginUrl(idpId);
  };

  // Button label : "Connexion fédérée" alone for a single IdP, numbered
  // ("Connexion fédérée 1", "Connexion fédérée 2"...) when several are
  // registered. The IdP description (or id) is shown as a hint.
  const idpLabel = (index) =>
    idps.length > 1 ? `Connexion fédérée ${index + 1}` : "Connexion fédérée";

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!username || !password) {
      setError("Veuillez remplir tous les champs");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const unscopedData = await loginWithCredentials({ username, password });
      setSessionCredentials(username, password);
      localStorage.setItem(
        "user",
        JSON.stringify(unscopedData?.user?.username || username)
      );

      const availableProjects = unscopedData?.user?.projects || [];
      const preferredProject =
        unscopedData?.user?.project_name || availableProjects?.[0]?.name;

      if (!preferredProject) {
        throw new Error("Aucun projet disponible pour créer un token scoped");
      }

      const scopedData = await loginWithCredentials({
        username,
        password,
        project: preferredProject,
      });

      setAuthData(scopedData);
      setActiveProject(preferredProject);

      navigate("/buckets");
    } catch (err) {
      setError(err.message || "Identifiants incorrects");
      console.error("Login error:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto py-12">
      {/* Header du formulaire */}
      <div className="text-center mb-10">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-amber-500 to-orange-600 shadow-lg mb-4">
          <Lock className="text-white w-8 h-8" />
        </div>
        <h2 className="text-3xl font-extrabold text-gray-800 tracking-tight">
          Connexion
        </h2>
        <p className="text-gray-500 mt-2">
          Accédez à votre espace de données MIDOC
        </p>
      </div>

      {/* Connexions fédérées en premier (méthode principale) : un bouton par
          identity provider enregistré dans Keystone. */}
      {ssoEnabled && (
        <div className="mb-6 space-y-3">
          {idps.map((idp, index) => (
            <button
              key={idp.id}
              type="button"
              onClick={() => handleSsoLogin(idp.id)}
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 py-4 bg-gradient-to-r from-amber-600 to-orange-600 hover:from-amber-700 hover:to-orange-700 text-white font-bold rounded-xl shadow-lg shadow-orange-200 transition-all duration-300 hover:scale-[1.02] active:scale-[0.98] disabled:opacity-70 disabled:cursor-not-allowed"
            >
              <KeyRound className="w-5 h-5" />
              <span>{idpLabel(index)}</span>
              <span className="text-white/70 text-xs font-medium">
                {idp.description || idp.id}
              </span>
            </button>
          ))}

          {!showClassic && (
            <>
              <div className="relative flex items-center my-6">
                <div className="flex-grow border-t border-gray-200"></div>
                <span className="flex-shrink mx-4 text-xs text-gray-400 uppercase tracking-widest font-semibold">
                  ou
                </span>
                <div className="flex-grow border-t border-gray-200"></div>
              </div>

              <button
                type="button"
                onClick={() => setShowClassic(true)}
                disabled={loading}
                className="w-full flex items-center justify-center gap-2 py-4 bg-white border border-gray-200 hover:border-orange-400 text-gray-700 font-bold rounded-xl shadow-sm transition-all duration-200 hover:scale-[1.01] active:scale-[0.98] disabled:opacity-70 disabled:cursor-not-allowed"
              >
                <User className="w-5 h-5 text-orange-500" />
                Connexion locale
              </button>
            </>
          )}
        </div>
      )}

      {/* Formulaire user/password (comptes locaux Keystone) : affiché
          directement si pas de SSO, sinon après clic sur "Connexion locale". */}
      {(!ssoEnabled || showClassic) && (
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Champ Utilisateur */}
        <div className="space-y-2">
          <label className="text-sm font-semibold text-gray-700 ml-1">
            Utilisateur
          </label>
          <div className="relative group">
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
              <User className="h-5 w-5 text-gray-400 group-focus-within:text-orange-500 transition-colors" />
            </div>
            <input
              type="text"
              placeholder="Compte"
              className="block w-full pl-11 pr-4 py-3 bg-white/50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-orange-500 focus:border-transparent outline-none transition-all duration-200 placeholder:text-gray-400"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              disabled={loading}
            />
          </div>
        </div>

        {/* Champ Mot de passe */}
        <div className="space-y-2">
          <label className="text-sm font-semibold text-gray-700 ml-1">
            Mot de passe
          </label>
          <div className="relative group">
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
              <Lock className="h-5 w-5 text-gray-400 group-focus-within:text-orange-500 transition-colors" />
            </div>
            <input
              type="password"
              placeholder="••••••••"
              className="block w-full pl-11 pr-4 py-3 bg-white/50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-orange-500 focus:border-transparent outline-none transition-all duration-200 placeholder:text-gray-400"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={loading}
            />
          </div>
        </div>

        {/* Message d'erreur */}
        {error && (
          <div className="flex items-center gap-3 p-4 bg-red-50 border border-red-100 text-red-600 rounded-xl animate-shake">
            <AlertCircle size={18} />
            <span className="text-sm font-medium">{error}</span>
          </div>
        )}

        {/* Bouton de soumission */}
        <button
          type="submit"
          disabled={loading}
          className="w-full relative group flex items-center justify-center gap-2 py-4 bg-gradient-to-r from-amber-600 to-orange-600 hover:from-amber-700 hover:to-orange-700 text-white font-bold rounded-xl shadow-lg shadow-orange-200 transition-all duration-300 hover:scale-[1.02] active:scale-[0.98] disabled:opacity-70 disabled:cursor-not-allowed"
        >
          {loading ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : (
            <>
              Se connecter
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </>
          )}
        </button>

        {/* Retour vers les méthodes de connexion (si SSO dispo) */}
        {ssoEnabled && (
          <button
            type="button"
            onClick={() => setShowClassic(false)}
            disabled={loading}
            className="w-full text-center text-sm text-gray-500 hover:text-orange-600 transition-colors"
          >
            ← Autres méthodes de connexion
          </button>
        )}
      </form>
      )}

      <p className="text-center mt-8 text-xs text-gray-400 uppercase tracking-widest font-semibold">
        Un texte centré
      </p>
    </div>
  );
};

export default Login;
