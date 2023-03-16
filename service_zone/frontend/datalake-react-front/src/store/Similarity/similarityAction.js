import {EDIT_LIST_SIMILARITY} from "./types";

export const editSimilarity = (similarity) => {
    return {
        type: EDIT_LIST_SIMILARITY,
        payload: similarity,
    }
}
