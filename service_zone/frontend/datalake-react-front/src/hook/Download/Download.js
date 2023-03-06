import api from "../../api/api";
import $ from "jquery";

export const downloadZipRaw = (body) => {
    return api.post('swift-files', body)
        .then((response) => {
            let url = response.data.swift_zip
            const link = document.createElement('a');
            link.href = url;
            link.click();
            window.URL.revokeObjectURL(url);
        })
        .catch(function (error) {
            console.log(error);
        });
}

export const downloadHandle = (body) => {
    return api.post('handled-data-file', body, {
        responseType: 'arraybuffer'
    })
        .then(function (result) {
            const url = window.URL.createObjectURL(new Blob([result.data], {type: 'application/zip'}));
            let link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', 'file.zip'); //or any other extension
            link.click();
            document.body.appendChild(url);
            return {result: true};
        })
        .catch(function (error, status) {
            console.error(status, error.toString()); // eslint-disable-line
        });
}

export const rawData = (url, data) => {
    console.log(data)
    const call = url + '/raw-data';
    $.ajax({
        url: call,
        data: data,
        xhrFields: {
            withCredentials: true
        },
        crossDomain: true,
        contentType: 'application/json; charset=utf-8',
        dataType: 'json',
        type: 'POST',

        success: (d) => {
            if (d.result) {
                return {
                    elements: d.result.objects,
                    totalLength: d.result.length,
                    pageCount: Math.ceil(d.result.length / this.state.perPage),
                };
            }
        },

        error: (xhr, status, err) => {
            console.error(this.url, status, err.toString()); // eslint-disable-line
        }
    });
}
export const handledData = (url, data) => {
    const call = url + '/handled-data-list';
    $.ajax({
        url: call,
        data: data,
        xhrFields: {
            withCredentials: true
        },
        crossDomain: true,
        contentType: 'application/json; charset=utf-8',
        dataType: 'json',
        type: 'POST',

        success: (data) => {
            if (!data.error) {
                let resultsData = this.prepareData(data)
                return {
                    elements: resultsData,
                    totalLength: Object.keys(data).length,
                    pageCount: Math.ceil(Object.keys(data).length / this.state.perPage),
                };
            }
        },

        error: (xhr, status, err) => {
            console.error(this.url, status, err.toString()); // eslint-disable-line
        }
    });
}
