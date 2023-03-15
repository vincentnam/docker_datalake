import api from "../../api/api";
import moment from "moment";

export const measurementsSGE = (token) => {
    return api.post('measurementsSGE', {
        token: localStorage.getItem('token')
    })
        .then((response) => {
            return {
                measurements: response.data.measurements,
                topics: [],
                measurement: ""
            };
        })
        .catch(function (error) {
            return {
                measurements: [],
                topics: [],
                measurement: ""
            };
        });
}

export const topicsSGE = (measurement, token) => {
    return api.post('topicsSGE', {
        measurement: measurement,
        token: localStorage.getItem('token')
    })
        .then((response) => {
            return {
                topics: response.data.topics,
                topic: "",
            };
        })
        .catch(function (error) {
            return {
                topics: [],
                topic: "",
            };
        });
}

export const dataSGE = (measurement, topic, startDate, endDate, token) => {
    return api.post('dataSGE', {
        measurement: measurement,
        topic: topic,
        startDate: moment(startDate).format('X'),
        endDate: moment(endDate).format('X'),
        token: token
    })
        .then((response) => {
            let result = [];
            for (const value of Object.entries(response.data.dataSGE[0])) {
                result.push(value[1]);
            }
            let data = []
            result.forEach((dt) => {
                data.push({
                    _time: moment.unix(dt._time / 1000).format("DD/MM/YYYY HH:mm:ss"),
                    _value: dt._value,
                    _measurement: dt._measurement,
                    topic: dt.topic,
                })
            });
            return {
                data: data,
                dataGraph: response.data.dataSGEGraph[0]
            }
        })
        .catch(function (error) {
            return {
                data: [],
                dataGraph: []
            }
        });
}


export const measurementsSensors = (nameContainer, token) => {
    return api.post('measurements', {
        bucket: nameContainer,
        token: token
    })
        .then((response) => {
            return {
                measurements: response.data.measurements
            };
        })
        .catch(function (error) {
            return {
                measurements: []
            };
        });
}
export const topicsSensors = (nameContainer, token, measurement) => {
    return api.post('topics', {
        bucket: nameContainer,
        token: token,
        measurement: measurement
    })
        .then((response) => {
            return {
                topics: response.data.topics
            };
        })
        .catch(function (error) {
            return {
                topics: []
            };
        });
}

export const dataSensors = (bucket, measurement, topic, startDate, endDate, token) => {
    return api.post('dataTimeSeries', {
        bucket: bucket,
        measurement: measurement,
        topic: topic,
        startDate: moment(startDate).format('X'),
        endDate: moment(endDate).format('X'),
        token: token
    })
        .then((response) => {
            let result = [];
            for (const value of Object.entries(response.data.dataTimeSeries[0])) {
                result.push(value[1]);
            }
            let data = []
            result.forEach((dt) => {
                data.push({
                    _time: moment.unix(dt._time / 1000).format("DD/MM/YYYY HH:mm:ss"),
                    _value: dt._value,
                    _measurement: dt._measurement,
                    topic: dt.topic,
                })
            });
            return {
                data: data,
                dataGraph: response.data.dataTimeSeriesGraph[0]
            }
        })
        .catch(function (error) {
            return {
                data: [],
                dataGraph: []
            }
        });
}