import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { User, Lock, ArrowRight, Loader2, AlertCircle } from "lucide-react";
import {
  setActiveProject,
  setAuthData,
  setSessionCredentials,
} from "../utils/authUtils";
import { loginWithCredentials } from "../utils/apiClient";

const Login = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

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
      </form>

      <p className="text-center mt-8 text-xs text-gray-400 uppercase tracking-widest font-semibold">
        Un texte centré
      </p>
    </div>
  );
};

export default Login;
