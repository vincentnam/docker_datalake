import {EDIT_NAME_CONTAINER, EDIT_LIST_CONTAINER } from "./types";

const initialState = {
    nameContainer: "",
    listProjectsAccess: []
};

export function containerReducer(state = initialState, action) {
    switch(action && action.type) {
        case EDIT_NAME_CONTAINER:
            return {
                ...state,
                nameContainer: action.payload
            };
        case EDIT_LIST_CONTAINER:
            return {
                ...state,
                listProjectsAccess: action.payload
            };
        default:
            return state;
    }
}
