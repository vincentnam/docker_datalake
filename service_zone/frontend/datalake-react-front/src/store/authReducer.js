import { EDIT_AUTH_PROJECTS, EDIT_AUTH_ROLES, EDIT_AUTH_TOKEN, EDIT_AUTH_LOGIN } from "./types"

const initialState = {
    token: "",
    projects: [],
    roles: [],
    isLogin: false
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
        case EDIT_AUTH_LOGIN:
            return {
                ...state,
                isLogin: action.payload
            };
        default:
            return state;
    }
}