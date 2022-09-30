import { EDIT_AUTH_PROJECTS, EDIT_AUTH_ROLES, EDIT_AUTH_TOKEN, EDIT_AUTH_LOGIN_ADMIN } from "./types"

const initialState = {
    isLoginAdmin: false,
    token: "",
    projects: [],
    roles: []
};

export function authReducer(state = initialState, action) {
    switch(action && action.type) {
        case EDIT_AUTH_PROJECTS:
            return {
                ...state,
                projects: action.payload
            };
        case EDIT_AUTH_ROLES:
            return {
                ...state,
                roles: action.payload
            };
        case EDIT_AUTH_TOKEN:
            return {
                ...state,
                token: action.payload
            };
        case EDIT_AUTH_LOGIN_ADMIN:
            return {
                ...state,
                isLoginAdmin: action.payload
            };
        default:
            return state;
    }
}