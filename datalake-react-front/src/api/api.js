import axios from 'axios';

export default function api(config={}){
    const defaultConfig = {
        baseURL: "",
        headers: {
            Accept: "application/json",
        }
    }
    if(config.auth){
        const token = "";
        defaultConfig.headers.Authorization = `${token}`;
    }

    return axios.create({ ...defaultConfig });
}