import api from "../../api/api";

export const object_id_big_file = (token) => {
    return api.post('object_id_big_file', {
        token: token
    })
        .then((response) => {
            return {id_file: response.data.object_id_big_file + 1}
        }).catch(function (error) {
        console.log(error);
            return {id_file: 0}
    });
}

export const modelsParams = (types_files, container_name, token) => {
    return api.post('models/params', {
        types_files: types_files,
        container_name: container_name,
        token: token
    })
        .then((response) => {
            return {models: response.data.models.data}
        }).catch(function (error) {
            return {models: []}
        });
}

export const model = (id, token) => {
    return api.post('models/id', {
        id: id,
        token: token
    })
        .then((response) => {
            return {
                othermeta: response.data.model.metadonnees,
                editModel: {
                    id: response.data.model._id,
                    label: response.data.model.label,
                    typesFiles: response.data.model.type_file_accepted,
                    metadonnees: response.data.model.metadonnees,
                    status: response.data.model.status,
                }
            }
        }).catch(function (error) {
            return {
                othermeta: [],
                editModel: {
                    id: "",
                    label: "",
                    typesFiles: [],
                    metadonnees: [],
                    status: false,
                }
            }
        });
}

export const storage = (idType, typeFile, filename, file, linkFile, linkType, othermeta, container_name, token) => {
    return api.post('storage', {
        idType: idType,
        typeFile: typeFile,
        filename: filename,
        file: file,
        linkFile: linkFile,
        linkType: linkType,
        othermeta: othermeta,
        container_name: container_name,
        token: token
    })
        .then((response) => {
            return {result: true}
        }).catch(function (error) {
            console.log(error);
        });
}
