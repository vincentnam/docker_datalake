export const initialState = {
    nameContainer: "neOCampus",
};

export function reducer(state, action) {
    // si l'action est de type changeNameContainer...
    if (action.type === "changeNameContainer") {
        return {
            ...state,
            nameContainer: action.payload.nameContainer
        };
    }
    // sinon on retourne le state sans le changer
    return state;
}


