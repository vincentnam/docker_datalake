import axios from 'axios';

export default axios.create({
    baseURL: process.env.REACT_APP_SERVER_NAME,
    headers: {
        'Accept': "application/json",
        'Access-Control-Allow-Origin': "*",
    }
});