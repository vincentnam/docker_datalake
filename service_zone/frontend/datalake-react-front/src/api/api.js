import axios from 'axios';

export default axios.create({
    baseURL: `http://neocampus-datalake-mongodb.dev.modiscloud.net/`,
    headers: {
        'Accept': "application/json",
        'Access-Control-Allow-Origin': "*",
    }
});