import {EDIT_AUTH_PROJECTS, EDIT_AUTH_ROLES, EDIT_AUTH_TOKEN, EDIT_AUTH_LOGIN_ADMIN} from "./types"

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

export const editAuthLoginAdmin = (isLoginAdmin) => {
    return {
        type: EDIT_AUTH_LOGIN_ADMIN,
        payload: isLoginAdmin,
    }
}