import React, {useEffect, useRef, useState} from 'react';
import './d3component_testfield.css'
import $ from "jquery"

import 'react-dropzone-uploader/dist/styles.css'
import ProgressBar from "./progressBar";


export default function D3Test(props) {
    const d3Container = useRef(null);
    const fileInputRef = useRef(null);
    // list of file in the dropzone
    const [file_array, setFileArray] = useState([])
    // used in onDragLeave onDragOver onMouseOut onMouseOver
    const [Highligth, setHighligth] = useState(false)
    // used in onDrop
    const [Highlight_drop, setHighlight_drop] = useState(false)
    //
    const [uploading, setUploading] = useState(false)
    // used in renderProgress
    const [uploadProgress, setUploadProgress] = useState({})

    const [successfullUploaded, setSuccessfullUploaded] = useState(false)
    const [disabled, setDisabled] = useState(false)
    const fileListToArray = (list) => {
        const array = file_array;
        for (var i = 0; i < list.length; i++) {
            array.push(list.item(i));
        }
        setFileArray(array)
        console.log(file_array)
    }
    const onFilesAdded = (evt) => {
        if (disabled) return;

        const files = evt.target.files;

        // setUploadProgress(upload_progress)

        fileListToArray(files);

        const prog_map = uploadProgress
        for (var i = 0; i < files.length; i++) {

            prog_map[files.item(i).name] = {state: "ready", percentage: 0}
        }
        setUploadProgress(prog_map)
    }
    const openFileDialog = () => {
        if (props.disabled) return;
        fileInputRef.current.click();
    }

    const onDrop = (evt) => {
        evt.preventDefault();

        if (disabled) return;

        const files = evt.dataTransfer.files;
        if (props.onFilesAdded) {
            const array = fileListToArray(files);
            props.onFilesAdded(array);
        }
        setHighlight_drop(true)
    }
    const onDragLeave = () => {
        setHighligth(false)
    }
    const onDragOver = (evt) => {
        evt.preventDefault();
        setHighligth(true)
    }
    const onMouseOut = () => {

        setHighligth(false)
    }
    const onMouseOver = () => {

        setHighligth(true)
    }


    // UPDATE WHEN SUCCESSFULLUPLOADED DICT IS FILLED
    const renderActions = () => {
        if (successfullUploaded) {
            return (
                <button
                    onClick={() => {
                        setFileArray([])
                        setSuccessfullUploaded(false)
                    }

                    }
                >
                    Clear
                </button>
            );
        } else {
            return (
                <button
                    disabled={file_array.length < 0 || uploading}
                    onClick={uploadFiles}
                >
                    Upload
                </button>
            );
        }
    }
    // receives array of files that are done uploading when submit button is clicked
    //
    const sendRequest = async (file) => {
        return new Promise((resolve, reject) => {
            console.log(file)
            const req = new XMLHttpRequest();
            const formdata = new FormData()

            const blob = new Blob([file], {type: "application/octet-stream", name: file.name})

            formdata.append("file", blob)
            $.ajax({
                url: "http://127.0.0.1:5000/upload_file",
                type: "POST",
                data: file,
                cache: false,
                processData: false,
                contentType: "application/octet-stream",
                xhr: function () {
                    var xhr = new XMLHttpRequest();
                    //Upload progress
                    xhr.upload.addEventListener("progress", function (evt) {
                        if (evt.lengthComputable) {
                            var percentComplete = (evt.loaded / evt.total) * 100 ;
                            //Do something with upload progress
                            console.log(percentComplete);
                            uploadProgress[file.name].percentage = percentComplete
                            console.log(uploadProgress[file.name])
                        }
                    }, false);
                    //Download progress
                    xhr.addEventListener("progress", function (evt) {
                        if (evt.lengthComputable) {
                            var percentComplete = (evt.loaded / evt.total) * 100;
                            //Do something with download progress
                            console.log(percentComplete);
                        }
                    }, false);
                    return xhr;
                },


            }).done(function (data) {
                console.log(data)
            })
        });
    }
    const uploadFiles = async () => {
        // setUploadProgress({uploadProgress: {}});
        setUploading(true)
        const promises = [];
        file_array.forEach(file => {
            promises.push(sendRequest(file));
        });
        try {
            await Promise.all(promises);
            setSuccessfullUploaded(true)
            setUploading(false)

        } catch (e) {
            // Not Production ready! Do some error handling here instead...
            setSuccessfullUploaded(false)
            setUploading(false)
            console.log(e)
            // this.setState({ successfullUploaded: true, uploading: false });
        }
    }

    return (
        <div className={"Card"}>
            <div className="Upload">
                <span className="Title">Drag'n'drop input file zone</span>
                <div className={`Dropzone ${Highligth ? "Highlight" : ""} ${Highlight_drop ? "Highlight_drop" : ""}`}
                     onDragOver={onDragOver}
                     onDragLeave={onDragLeave}
                     onDrop={onDrop}
                     onClick={openFileDialog}
                     onMouseOver={onMouseOver}
                     onMouseOut={onMouseOut}

                     style={{cursor: props.disabled ? "default" : "pointer"}}>
                    <img alt="upload"
                         className="Icon"
                         src={require("./dropzone/images/folder.svg")}/>
                    <input
                        ref={fileInputRef}
                        className="FileInput"
                        type="file"
                        multiple
                        onChange={onFilesAdded}
                    />

                    <span>Upload Files</span>
                </div>

                <div className="Content">
                    <div>

                    </div>
                    <div className="Files">
                        {file_array.map(file => {
                            return (
                                <div key={file.name} className="Row">
                                    <span className="Filename">{file.name + " " +uploadProgress[file.name].percentage + " %"} </span>
                                    {/*{renderProgress(file)}*/}

                                    <div className="ProgressWrapper">
                                        <ProgressBar progress={50} />
                                        <img
                                            className="CheckIcon"
                                            alt="done"
                                            src="dropzone/images/checked.svg"
                                            style={{
                                                opacity:
                                                    uploadProgress && uploadProgress[file.name].state === "done" ? 0.5 : 0
                                            }}
                                        />
                                    </div>

                                </div>
                            );
                        })}

                    </div>
                </div>
                <div className="Actions">{renderActions()}</div>
            </div>
        </div>


    )


}












