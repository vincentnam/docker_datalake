import api from "../../api/api";

export const loadListTraceability = (nameContainer, token) => {
    return api.post('uploadssh', {
        container_name: nameContainer,
        token: token
    })
        .then((response) => {
            return {
                traceability: response.data.file_upload,
                traceability_finished: response.data.file_upload_finished
            };
        })
        .catch(function (error) {
            console.log(error);
            return {
                traceability: [],
                traceability_finished: []
            };
        });
}
