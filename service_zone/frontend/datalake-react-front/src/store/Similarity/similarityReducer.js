import {EDIT_LIST_SIMILARITY} from "./types";

const initialState = {
    similarity: []
};

export function similarityReducer(state = initialState, action) {
    switch(action && action.type) {
        case EDIT_LIST_SIMILARITY:
            return {
                ...state,
                similarity: action.payload
            };
        default:
            return state;
    }
}