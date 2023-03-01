import api from "../../api/api";

export const anomaliesAll = (nameContainer, token) => {
    return api.post('getDataAnomalyAll', {
        container_name: nameContainer,
        token: token
    })
        .then((response) => {
            let result = [];
            for (const value of Object.entries(response.data.anomaly.objects)) {
                result.push(value[1]);
            }
            let all_data = []
            result.forEach((dt) => {
                //console.log(dt)
                all_data.push({
                    _id: dt._id,
                    _topic: dt.topic,
                    _value: dt.value,
                    _unit: dt.unit,
                    _datetime: dt.datetime,
                    _startDate_detection: dt.startDate_detection,
                    _endDate_detection: dt.endDate_detection,
                })
            });
            return {
                dataFilters: all_data
            };
        })
        .catch(function (error) {
            console.log(error);
        });
}

export const dataAnomalyAll = (container_name, token ) => {
    return api.post('getDataAnomalyAll', {
        container_name: container_name,
        token: token
    })
        .then((response) => {
            return {
                anomalies: response.data.anomaly
            }
        })
        .catch(function (error) {
            console.log(error);
        });
}

export const anomaliesGet = (measurement, topic, startDate, endDate, nameContainer, token) => {
    return api.post('getDataAnomaly', {
        measurement: measurement,
        topic: topic,
        startDate: startDate,
        endDate: endDate,
        container_name: nameContainer,
        token: token
    })
        .then((response) => {
            let result = [];
            for (const value of Object.entries(response.data.anomly.objects)) {
                result.push(value[1]);
            }
            let data = []
            result.forEach((dt) => {
                data.push({
                    _id: dt._id,
                    _topic: dt.topic,
                    _value: dt.value,
                    _unit: dt.unit,
                    _datetime : dt.datetime,
                    _startDate_detection: dt.startDate_detection,
                    _endDate_detection: dt.endDate_detection,
                    //...
                })
            });
            return {
                data: data
            };
        })
        .catch(function (error) {
            console.log(error);
        });
}

export const measurementsAll = (nameContainer, token) => {
    return api.post('measurements', {
        bucket: nameContainer,
        token: token
    })
        .then((response) => {
            return {
                measurements: response.data.measurements,
                topics: [],
                measurement: ""
            };
        })
        .catch(function (error) {
            console.log(error);
        });
}
export const topicsAll = (nameContainer, token, measurement) => {
    return api.post('topics', {
        bucket: nameContainer,
        token: token,
        measurement: measurement
    })
        .then((response) => {
            return {
                topics: response.data.topics,
                topic: "",
            };
        })
        .catch(function (error) {
            console.log(error);
        });
}