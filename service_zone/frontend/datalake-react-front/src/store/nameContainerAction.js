import { EDIT_NAME_CONTAINER, EDIT_LIST_CONTAINER } from "./types"

export const editNameContainer = (nameContainer) => {
    return {
        type: EDIT_NAME_CONTAINER,
        payload: nameContainer,
    }
}

export const editListProjectAccess = (projects) => {
    return {
        type: EDIT_LIST_CONTAINER,
        payload: projects,
    }
}