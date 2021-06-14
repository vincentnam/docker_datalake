import React, { Component } from "react";
import Dropzone from "./Dropzone";
import "./Upload.css";
import Progress from "./Progress";
import $ from "jquery";
class Upload extends Component {
    constructor(props) {
        super(props);
        this.state = {
            files: [],
            uploading: false,
            uploadProgress: {},
            successfullUploaded: false
        };

        this.onFilesAdded = this.onFilesAdded.bind(this);
        this.uploadFiles = this.uploadFiles.bind(this);
        this.sendRequest = this.sendRequest.bind(this);
        this.renderActions = this.renderActions.bind(this);
    }

    onFilesAdded(files) {
        this.setState(prevState => ({
            files: prevState.files.concat(files)
        }));
    }

    async uploadFiles() {
        this.setState({ uploadProgress: {}, uploading: true });
        const promises = [];
        this.state.files.forEach(file => {
            promises.push(this.sendRequest(file));
        });
        try {
            await Promise.all(promises);

            this.setState({ successfullUploaded: true, uploading: false });
        } catch (e) {
            // Not Production ready! Do some error handling here instead...
            this.setState({ successfullUploaded: true, uploading: false });
        }
    }

    sendRequest(file) {
        return new Promise((resolve, reject) => {
            const req = new XMLHttpRequest();

            const form = new FormData();
            form.append("file",file,file.name)
            $.ajax({
                url: "http://127.0.0.1:5000/upload_file",
                type: "POST",
                data: file,
                cache: false,
                processData: false,
                context: this,
                // filename:file.name,
                // contentType:"multipart/form-data",
                contentType: "application/octet-stream",
                headers: {
                    "filename":file.name
                },
                xhr: function () {
                    var req = new XMLHttpRequest();
                    console.log(this)
                    //Upload progress
                    req.upload.addEventListener("progress", event => {
                        if (event.lengthComputable) {
                            const copy = { ...this.context.state.uploadProgress };
                            copy[file.name] = {
                                state: "pending",
                                percentage: (event.loaded / event.total) * 100
                            };
                            this.context.setState({ uploadProgress: copy });
                            this.context.forceUpdate()
                            console.log(copy[file.name])
                        }
                    });

                    req.upload.addEventListener("load", event => {
                        const copy = { ...this.context.state.uploadProgress };
                        copy[file.name] = { state: "done", percentage: 100 };
                        this.context.setState({ uploadProgress: copy });
                        resolve(req.response);
                    });

                    req.upload.addEventListener("error", event => {
                        const copy = { ...this.context.state.uploadProgress };
                        copy[file.name] = { state: "error", percentage: 0 };
                        this.context.setState({ uploadProgress: copy });
                        reject(req.response);
                    });
                    return req;
                },


            }).promise()
        });
    }

    renderProgress(file) {
        const uploadProgress = this.state.uploadProgress[file.name];
        if (this.state.uploading || this.state.successfullUploaded) {
            return (
                <div className="ProgressWrapper">
                    <Progress progress={uploadProgress ? uploadProgress.percentage : 0} />
                </div>
            );
        }
    }

    renderActions() {
        if (this.state.successfullUploaded) {
            return (
                <button
                    onClick={() =>
                        this.setState({ files: [], successfullUploaded: false })
                    }
                >
                    Clear
                </button>
            );
        } else {
            return (
                <button
                    disabled={this.state.files.length < 0 || this.state.uploading}
                    onClick={this.uploadFiles}
                >
                    Upload
                </button>
            );
        }
    }

    render() {
        return (
            <div className="Upload">
                <span className="Title">Upload Files</span>
                <div className="Content">
                    <div>
                        <Dropzone
                            onFilesAdded={this.onFilesAdded}
                            disabled={this.state.uploading || this.state.successfullUploaded}
                        />
                    </div>
                    <div className="Files">
                        {this.state.files.map(file => {
                            return (
                                <div key={file.name} className="Row">
                                    <span className="Filename">{file.name}</span>
                                    {this.renderProgress(file)}
                                </div>
                            );
                        })}
                    </div>
                </div>
                <div className="Actions">{this.renderActions()}</div>
            </div>
        );
    }
}

export default Upload;
