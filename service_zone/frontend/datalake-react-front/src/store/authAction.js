import { EDIT_AUTH_PROJECTS, EDIT_AUTH_ROLES, EDIT_AUTH_TOKEN } from "./types"

export const editAuthToken = (token) => {
    return {
        type: EDIT_AUTH_TOKEN,
        payload: token,
    }
}

export const editAuthProjects = (projects) => {
    return {
        type: EDIT_AUTH_PROJECTS,
        payload: projects,
    }
}

export const editAuthRoles = (roles) => {
    return {
        type: EDIT_AUTH_ROLES,
        payload: roles,
    }
}