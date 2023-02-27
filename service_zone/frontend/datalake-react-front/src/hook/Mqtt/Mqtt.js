import api from "../../api/api";

export const mqttAll = (nameContainer, token) => {
    return api.post('mqtt/all', {
        container_name: nameContainer,
        token: token
    })
        .then((response) => {
            return {
                elements: response.data.list_flux.data
            };
        })
        .catch(function (error) {
            console.log(error);
        });
}

export const mqttAllStatus = (nameContainer, token) => {
    return api.post('mqtt/status/actif', {
        container_name: nameContainer,
        token: token
    })
        .then((response) => {
            return {
                elements: response.data.list_flux.data
            };
        })
        .catch(function (error) {
            console.log(error);
        });
}

export const mqttAdd = (name, description, brokerUrl, user, password, topic, status, container_name, token) => {
    return api.post('mqtt/add', {
        name: name,
        description: description,
        brokerUrl: brokerUrl,
        user: user,
        password: password,
        topic: topic,
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

export const mqttEdit = (id, name, description, brokerUrl, user, password, topic, status, container_name, token) => {
    return api.post('mqtt/edit', {
        id: id,
        name: name,
        description: description,
        brokerUrl: brokerUrl,
        user: user,
        password: password,
        topic: topic,
        container_name: container_name,
        status: status,
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

export const mqttEditStatus = (id, status, token) => {
    return api.post('mqtt/status/change', {
        id: id,
        status: status,
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