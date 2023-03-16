import {EDIT_LIST_TRACEABILITY} from "./types";
import api from "../../api/api";

export const editTraceability = async (nameContainer, token) => {
    console.log(nameContainer);
    console.log(token);
    api.post('uploadssh', {
        container_name: nameContainer,
        token: token
    })
        .then((response) => {
            console.log(response)
            return {
                type: EDIT_LIST_TRACEABILITY,
                payload: {
                    elements: response.data.file_upload,
                    elements_finished: response.data.file_upload_finished
                },
            }
        })
        .catch(function (error) {
            console.log(error);
        });
}
