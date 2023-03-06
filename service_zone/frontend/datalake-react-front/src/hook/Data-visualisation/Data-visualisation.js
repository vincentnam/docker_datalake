import api from "../../api/api";
import moment from "moment";

export const measurements = (token) => {
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
            console.log(error);
        });
}

export const topics = (measurement, token) => {
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
            console.log(error);
        });
}

export const dataSGE = (measurement, topic, startDate, endDate, token) => {
    return api.post('dataSGE', {
        measurement: this.state.measurement,
        topic: this.state.topic,
        startDate: moment(startDate).format('X'),
        endDate: moment(endDate).format('X'),
        token: localStorage.getItem('token')
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
            console.log(error);
        });
}