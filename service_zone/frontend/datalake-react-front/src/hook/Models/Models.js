import api from "../../api/api";

export const modelsAll = (nameContainer, token) => {
    return api.post('models/all', {
        container_name: nameContainer,
        token: token
    })
        .then((response) => {
            return {
                verifModels: response.data.models.data
            };
        })
        .catch(function (error) {
            console.log(error);
        });
}
export const modelsShowAll = (nameContainer, token) => {
    return api.post('models/show/all', {
        container_name: nameContainer,
        token: token
    })
        .then((response) => {
            return {
                models: response.data.models.data,
            };
        })
        .catch(function (error) {
            console.log(error);
        });
}


export const modelsCacheAll = (nameContainer, token) => {
    return api.post('models/cache/all', {
        container_name: nameContainer,
        token: token
    })
        .then((response) => {
            return {
                modelsCache: response.data.models.data
            };
        })
        .catch(function (error) {
            console.log(error);
        });
}

export const modelAdd = (label, type_file_accepted, metadonnees, status, container_name, token) => {
    return api.post('models/add', {
        label: label,
        type_file_accepted: type_file_accepted,
        metadonnees: metadonnees,
        status: status,
        container_name: container_name,
        token: token
    })
        .then(() => {
            return {
                result: true
            }
        })
        .catch(function (error) {
            console.log(error);
            return {
                result: false
            }
        });
}

export const modelEdit = (id, label, type_file_accepted, metadonnees, status, container_name, token) => {
    return api.post('models/edit', {
        id: id,
        label: label,
        type_file_accepted: type_file_accepted,
        metadonnees: metadonnees,
        status: status,
        container_name: container_name,
        token: token
    })
        .then(() => {
            return {
                result: true
            }
        })
        .catch(function (error) {
            console.log(error);
            return {
                result: false
            }
        });
}