import { EDIT_NAME_CONTAINER } from "./types"

export const editNameContainer = (nameContainer) => {
    return {
        type: EDIT_NAME_CONTAINER,
        payload: nameContainer,
    }
}