// #TODO: Refactor : move to ListObject folder
import React, { useCallback, useEffect, useMemo, useState } from "react";
import {
  addUserToProject,
  getAllUsers,
  getProjectMembers,
  getProjectRoles,
  removeUserFromProject,
  updateProjectUserRoles,
} from "../utils/projectAdminClient";
import { Shield, UserPlus, Users, PencilLine, X, Trash2 } from "lucide-react";

const normalizeRoleNames = (roles) =>
  roles
    .map((role) => {
      if (typeof role === "string") return role;
      if (role && typeof role.name === "string") return role.name;
      return null;
    })
    .filter(Boolean);

const ProjectAdministration = ({ projectName, showSuccess, showError }) => {
  const [members, setMembers] = useState([]);
  const [roles, setRoles] = useState([]);
  const [allUsers, setAllUsers] = useState([]);
  const [newUsername, setNewUsername] = useState("");
  const [loading, setLoading] = useState(false);
  const [savingRoles, setSavingRoles] = useState(false);

  const [editingUser, setEditingUser] = useState(null);
  const [editingRoles, setEditingRoles] = useState([]);

  const roleOptions = useMemo(() => {
    const names = normalizeRoleNames(roles);

    return names.length ? names : ["member"];
  }, [roles]);

  const rows = useMemo(
    () =>
      members.map((member) => ({
        id: member.id,
        name: member.name,
        roles: member.roles || [],
        isMember: true,
        memberId: member.id,
      })),
    [members]
  );

  const userNames = useMemo(() => allUsers.map((u) => u.name), [allUsers]);

  const loadAdminData = useCallback(async () => {
    if (!projectName) return;
    setLoading(true);
    try {
      const [membersData, rolesData, usersData] = await Promise.all([
        getProjectMembers(projectName),
        getProjectRoles(projectName),
        getAllUsers(),
      ]);
      setMembers(Array.isArray(membersData) ? membersData : []);
      setRoles(Array.isArray(rolesData) ? rolesData : []);
      setAllUsers(Array.isArray(usersData) ? usersData : []);
    } catch (error) {
      showError("Administration", error.message || "Erreur de chargement");
    } finally {
      setLoading(false);
    }
  }, [projectName, showError]);

  useEffect(() => {
    loadAdminData();
  }, [loadAdminData]);

  useEffect(() => {
    const onProjectChanged = () => {
      loadAdminData();
      closeRoleEditor();
    };
    window.addEventListener("projectChanged", onProjectChanged);
    return () => window.removeEventListener("projectChanged", onProjectChanged);
  }, [loadAdminData]);

  const handleAddUser = async () => {
    const username = newUsername.trim();
    if (!username) return;
    if (!userNames.includes(username)) {
      showError("Administration", "Selectionne un utilisateur existant");
      return;
    }
    try {
      await addUserToProject(projectName, username, "member");
      setNewUsername("");
      showSuccess("Administration", "Utilisateur ajoute (role member)");
      await loadAdminData();
    } catch (error) {
      showError("Administration", error.message || "Ajout impossible");
    }
  };

  const openRoleEditor = (userRow) => {
    setEditingUser(userRow);
    setEditingRoles(userRow.roles || []);
  };

  const closeRoleEditor = () => {
    setEditingUser(null);
    setEditingRoles([]);
  };

  const toggleRole = (roleName) => {
    setEditingRoles((prev) =>
      prev.includes(roleName) ? prev.filter((r) => r !== roleName) : [...prev, roleName]
    );
  };

  const saveRoles = async () => {
    if (!editingUser) return;
    setSavingRoles(true);
    try {
      await updateProjectUserRoles(projectName, editingUser.memberId, editingRoles);
      showSuccess("Administration", `Roles mis a jour pour ${editingUser.name}`);
      closeRoleEditor();
      await loadAdminData();
    } catch (error) {
      showError("Administration", error.message || "Modification impossible");
    } finally {
      setSavingRoles(false);
    }
  };

  const handleRemoveUser = async (row) => {
    if (!window.confirm(`Supprimer ${row.name} du projet ${projectName} ?`)) return;
    try {
      await removeUserFromProject(projectName, row.memberId);
      showSuccess("Administration", `${row.name} supprime du projet`);
      closeRoleEditor();
      await loadAdminData();
    } catch (error) {
      showError("Administration", error.message || "Suppression impossible");
    }
  };

  return (
    <section className="rounded-[2rem] border border-gray-100 bg-white shadow-xl shadow-gray-200/40">
      <div className="p-6 md:p-8">
        <div className="flex flex-col gap-6 md:flex-row md:items-end md:justify-between">
          <div>
            <div className="mb-2 inline-flex items-center gap-2 rounded-full border border-blue-100 bg-blue-50 px-3 py-1 text-[11px] font-bold uppercase tracking-widest text-blue-700">
              <Shield size={12} />
              Gouvernance
            </div>
            <h3 className="text-2xl font-black tracking-tight text-gray-900 uppercase">
              Administration des utilisateurs
            </h3>
            <p className="mt-1 text-sm text-gray-500">
              Projet actif: <span className="font-semibold text-gray-700">{projectName}</span>
            </p>
          </div>

          <div className="inline-flex items-center gap-2 rounded-xl border border-gray-200 bg-white px-3 py-2 text-xs font-semibold text-gray-600">
            <Users size={15} />
            {rows.length} utilisateurs
          </div>
        </div>

        <div className="mt-6 grid grid-cols-1 gap-3 md:grid-cols-[1fr_auto]">
          <input
            type="text"
            placeholder="Nom utilisateur a ajouter au projet"
            list="project-user-suggestions"
            value={newUsername}
            onChange={(e) => setNewUsername(e.target.value)}
            className="h-11 rounded-xl border border-gray-200 bg-white px-4 text-sm font-medium text-gray-700 outline-none ring-blue-200 transition focus:ring-2"
          />
          <datalist id="project-user-suggestions">
            {userNames.map((name) => (
              <option key={name} value={name} />
            ))}
          </datalist>
          <button
            onClick={handleAddUser}
            disabled={loading || !newUsername.trim()}
            className="inline-flex h-11 items-center justify-center gap-2 rounded-xl bg-blue-700 px-5 text-sm font-semibold text-white transition hover:bg-blue-800 disabled:cursor-not-allowed disabled:opacity-50"
          >
            <UserPlus size={15} />
            Ajouter (member)
          </button>
        </div>

        <div className="mt-6 overflow-x-auto rounded-2xl border border-gray-100 bg-white">
          <table className="min-w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-5 py-3 text-left text-[11px] font-black uppercase tracking-widest text-gray-500">
                  Utilisateur
                </th>
                <th className="px-5 py-3 text-left text-[11px] font-black uppercase tracking-widest text-gray-500">
                  Roles
                </th>
                <th className="px-5 py-3 text-right text-[11px] font-black uppercase tracking-widest text-gray-500">
                  Action
                </th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.id} className="border-t border-gray-100">
                  <td className="px-5 py-3">
                    <button
                      onClick={() => openRoleEditor(row)}
                      className="inline-flex items-center gap-2 font-semibold text-gray-800 transition hover:text-blue-700"
                    >
                      {row.name}
                      <PencilLine size={14} />
                    </button>
                  </td>
                  <td className="px-5 py-3">
                    <div className="flex max-w-full flex-wrap gap-2">
                      {(row.roles || []).length ? (
                        row.roles.map((role) => (
                          <span
                            key={`${row.id}-${role}`}
                            className="max-w-full break-all rounded-md border border-green-100 bg-green-50 px-2 py-1 text-[11px] font-bold uppercase tracking-wide text-green-700"
                          >
                            {role}
                          </span>
                        ))
                      ) : (
                        <span className="text-xs font-medium text-gray-400">Aucun role</span>
                      )}
                    </div>
                  </td>
                  <td className="px-5 py-3 text-right">
                    <div className="inline-flex items-center gap-2">
                      <button
                        onClick={() => openRoleEditor(row)}
                        className="rounded-lg border border-gray-200 bg-white px-3 py-1.5 text-xs font-semibold text-gray-600 transition hover:border-blue-200 hover:text-blue-700"
                      >
                        Modifier
                      </button>
                      <button
                        onClick={() => handleRemoveUser(row)}
                        className="inline-flex items-center gap-1 rounded-lg border border-red-100 bg-red-50 px-3 py-1.5 text-xs font-semibold text-red-600 transition hover:bg-red-100"
                      >
                        <Trash2 size={13} />
                        Supprimer
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
              {!rows.length && (
                <tr>
                  <td colSpan={3} className="px-5 py-8 text-center text-sm text-gray-400">
                    Aucun utilisateur trouve.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {editingUser && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/45 p-4">
          <div className="w-full max-w-md rounded-2xl border border-gray-200 bg-white p-6 shadow-2xl">
            <div className="mb-4 flex items-center justify-between">
              <div>
                <h4 className="text-lg font-black text-gray-900">Modifier les roles</h4>
                <p className="text-sm font-medium text-gray-500">{editingUser.name}</p>
              </div>
              <button
                onClick={closeRoleEditor}
                className="rounded-lg p-1.5 text-gray-500 transition hover:bg-gray-100 hover:text-gray-700"
              >
                <X size={18} />
              </button>
            </div>

            <div className="space-y-2">
              {roleOptions.filter((roleName) => !["admin", "service", "bucket_owner"].includes(roleName)).map((roleName) => {
                const checked = editingRoles.includes(roleName);
                return (
                  <label
                    key={roleName}
                    className="flex cursor-pointer items-center justify-between rounded-xl border border-gray-200 px-3 py-2 hover:border-blue-200 hover:bg-blue-50/60"
                  >
                    <span className="text-sm font-semibold text-gray-700">{roleName}</span>
                    <input
                      type="checkbox"
                      checked={checked}
                      onChange={() => toggleRole(roleName)}
                      className="h-4 w-4 accent-blue-600"
                    />
                  </label>
                );
              })}
            </div>

            <div className="mt-5 flex items-center justify-end gap-2">
              <button
                onClick={closeRoleEditor}
                className="rounded-lg border border-gray-200 px-4 py-2 text-sm font-semibold text-gray-600 hover:bg-gray-50"
              >
                Annuler
              </button>
              <button
                onClick={saveRoles}
                disabled={savingRoles}
                className="rounded-lg bg-blue-700 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-800 disabled:opacity-50"
              >
                Enregistrer
              </button>
            </div>
          </div>
        </div>
      )}
    </section>
  );
};

export default ProjectAdministration;
