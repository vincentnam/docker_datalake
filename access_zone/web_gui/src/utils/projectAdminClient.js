import { apiFetch } from "./apiClient";

export const getProjectMembers = async (projectName) => {
  const response = await apiFetch(`/projects/${encodeURIComponent(projectName)}/members`, {
    method: "GET",
  });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  const data = await response.json();
  return Array.isArray(data.members) ? data.members : [];
};

export const getProjectRoles = async (projectName) => {
  const response = await apiFetch(`/projects/${encodeURIComponent(projectName)}/roles`, {
    method: "GET",
  });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  const data = await response.json();
  return Array.isArray(data.roles) ? data.roles : [];
};

export const getAllUsers = async () => {
  const response = await apiFetch("/users", {
    method: "GET",
  });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  const data = await response.json();
  return Array.isArray(data) ? data : [];
};

export const addUserToProject = async (projectName, username, role = "member") => {
  const response = await apiFetch(`/projects/${encodeURIComponent(projectName)}/users`, {
    method: "POST",
    // #TODO: Change to header to unify
    body: JSON.stringify({ username, role }),
  });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
};

export const updateProjectUserRoles = async (projectName, userId, roles) => {
  const response = await apiFetch(
    `/projects/${encodeURIComponent(projectName)}/users/${encodeURIComponent(userId)}/roles`,
    {
      method: "PUT",
      body: JSON.stringify({ roles }),
    }
  );
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
};

export const removeUserFromProject = async (projectName, userId) => {
  const response = await apiFetch(
    `/projects/${encodeURIComponent(projectName)}/users/${encodeURIComponent(userId)}`,
    {
      method: "DELETE",
    }
  );
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
};
