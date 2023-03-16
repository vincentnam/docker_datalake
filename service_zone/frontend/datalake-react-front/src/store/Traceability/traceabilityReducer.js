import {EDIT_LIST_TRACEABILITY} from "./types";

const initialState = {
    traceability: [],
    traceability_finished: []
};

export function traceabilityReducer(state = initialState, action) {
    switch(action && action.type) {
        case EDIT_LIST_TRACEABILITY:
            return {
                ...state,
                traceability: action.payload.elements,
                traceability_finished: action.payload.elements_finished
            };
        default:
            return state;
    }
}