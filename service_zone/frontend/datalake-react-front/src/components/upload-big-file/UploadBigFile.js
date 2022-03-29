import React from "react"
import { connect } from "react-redux";
import Dropzone from "dropzone";

class UploadBigFile extends React.Component {

    constructor() {
        super();
    }

    componentDidMount(){
        Dropzone.options.dropper = {
            paramName: 'file',
            chunking: true,
            forceChunking: true,
            url: process.env.REACT_APP_SERVER_NAME + '/upload-big-file',
            maxFilesize: 3096, // megabytes
            chunkSize: 10000000 // bytes (10 MB)
        }

        const myDropzone = new Dropzone("#dropper");

        const output = document.querySelector("#output");

        myDropzone.on("addedfile", (file) => {
        // Add an info line about the added file for each file.
        output.innerHTML += `<div>File added: ${file.name}</div>`;
        });
    }

    render() {

        return(
            <div>
                 <form method="POST" action='/upload-big-file' class="dropzone dz-clickable" 
                    id="dropper" enctype="multipart/form-data">
                </form>

                <h1>Debug output:</h1>
                <pre id="output"></pre>
            </div>
        )
    }
}

const mapStateToProps = (state) => {
    return {
        nameContainer: state.nameContainer,
    }
}

export default connect(mapStateToProps, null)(UploadBigFile)