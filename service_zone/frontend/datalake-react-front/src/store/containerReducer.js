import {EDIT_NAME_CONTAINER } from "./types";

const initialState = {
    nameContainer: "neOCampus",
};

export function containerReducer(state = initialState, action) {
    switch(action && action.type) {
        case EDIT_NAME_CONTAINER:
            return {
                ...state,
                nameContainer: action.payload
            };
        default:
            return state;
    }
}
