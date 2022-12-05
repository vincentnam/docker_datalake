import React from "react";
import api from '../api/api';
import {connect} from "react-redux";
import {Dropzone as DropzoneBigData} from "dropzone";
import {toast, ToastContainer} from "react-toastify";

class Similarity extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            users: [],
            selectElement: {
                id: "",
                name: ""
            },
            selectElementAccess: {
                role: {name:""},
                project: {name:""}
            },
            userAccess: [],
            files: [],
            resultSimilarity: []
        };

        this.loadRolesProjectsUser = this.loadRolesProjectsUser.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
    }

    componentDidMount() {
        this.loadRolesProjectsUser();
        DropzoneBigData.options.dropper = {
            paramName: 'file',
            chunking: false,
            url: process.env.REACT_APP_SERVER_NAME + '/similarity',
            //acceptedFiles: ,
            maxFilesize: 1000000, // megabytes (1 000 000 MB = 1 To, for now but changer after)
            chunkSize: 10000000, // bytes (10 MB),
            autoProcessQueue: false, // disable upload automatically
            // eslint-disable-next-line no-multi-str
            dictDefaultMessage: " Veuillez glisser une image ici<br /> \
            ou<br /> \
            <u>cliquer pour ajouter une image</u><br /> \
            Formats suivants acceptés (.jpg, .jpeg, .png, .svg)",
            addRemoveLinks: true,
            acceptedFiles: "image/*"
        }

        const myDropzone = new DropzoneBigData("#dropper");

        this.setState({'dropper': myDropzone})

        //Message toast after add a file
        myDropzone.on("addedfile", file => {
            toast.success("L'image a bien été ajouter, veuillez cliquer sur le bouton pour lancer la similitude de l'image !", {
                theme: "colored",
                position: "top-right",
                autoClose: 8000,
                hideProgressBar: false,
                closeOnClick: true,
                pauseOnHover: false,
                draggable: true,
                progress: undefined,
            });
        });

        //Message after the file is completely upload
        myDropzone.on("success", (file, response) => {
            toast.success("Similitude terminée !", {
                theme: "colored",
                position: "top-right",
                autoClose: 10000,
                hideProgressBar: false,
                closeOnClick: true,
                pauseOnHover: false,
                draggable: true,
                progress: undefined,
            });
            console.log(response);
            console.log(JSON.parse(response)[0]);
            this.setState({'resultSimilarity': JSON.parse(response)[0]})
            myDropzone.removeFile(file);
        })
        //Message error if the file not correctly upload
        myDropzone.on("error", file => {
            toast.error("La similitude n'a pas réussi !", {
                theme: "colored",
                position: "top-right",
                autoClose: 10000,
                hideProgressBar: false,
                closeOnClick: true,
                pauseOnHover: false,
                draggable: true,
                progress: undefined,
            });
        })
    }

    loadRolesProjectsUser() {
        api.post('auth-token/projects', {
            token: localStorage.getItem('token')
        })
            .then((response) => {
                let listProjectAccess = [];
                response.data.projects.forEach((project) => {
                    if (project.name !== "datalake" && project.name !== "admin") {
                        listProjectAccess.push({
                            label: project.name,
                            name_container: project.name,
                        })
                    }
                });
                this.setState({
                    container_name: listProjectAccess[0].name_container,
                })
            })
            .catch(function (error) {
                console.log(error);
            });
    }


    handleSubmit(event) {
        event.preventDefault();
        let dropper = this.state.dropper;
        let nbErrors = 0;

        dropper.files.forEach((file) => {
            let typeFile = file.type;
            console.log(typeFile)
            let type_files_accepts = ["image/jpeg","image/png"]
            if (type_files_accepts.includes(typeFile) === false) {
                toast.error("Format de fichier non accepté. Veuillez ajouter un fichier qui correspond à un de ses types : " + type_files_accepts.join(' '), {
                    theme: "colored",
                    position: "top-right",
                    autoClose: 5000,
                    hideProgressBar: false,
                    closeOnClick: true,
                    pauseOnHover: true,
                    draggable: true,
                    progress: undefined,
                });
                nbErrors += 1;
            }
        });
        if (nbErrors === 0) {
            dropper.on("sending", function (file, xhr, formData) {
                let token = localStorage.getItem('token');
                formData.append('token', token);
            });

            dropper.processQueue();
            //Message to warn that the file is being uploaded
            toast.success("La similitude est en cours, veuillez patienter !", {
                theme: "colored",
                position: "top-right",
                autoClose: 7000,
                hideProgressBar: false,
                closeOnClick: true,
                pauseOnHover: false,
                draggable: true,
                progress: undefined,
            });
        }
    }

    render() {
        const ResultSimilarity = () => {
            if (this.state.resultSimilarity.length === 0) {
                return(<p></p>);
            } else {
                const listImages = this.state.resultSimilarity.map((image) => (
                    console.log(typeof image[1])
                    // eslint-disable-next-line jsx-a11y/img-redundant-alt
                    // <img src={'data:image/jpeg;base64,' + image[1]+"'"}  alt="Image result"/>
                ));
                return(<div>
                    {listImages}
                </div>);
            }
        }


        return (
            <>
                <div className="container main-upload">
                    <h3 className="mt-4">Similarity</h3>
                    <form onSubmit={this.handleSubmit}>
                        <form method="POST" action='/similarity'
                              className="dropzone dz-clickable"
                              id="dropper" encType="multipart/form-data">
                        </form>
                        <div className="d-flex justify-content-around align-content-center mt-2">
                            <div className="d-md-flex justify-content-center">
                                <button type="submit" className="btn btn-oran">Valider</button>
                            </div>
                        </div>
                    </form>

                    <h4>Résultats : </h4>
                    <ResultSimilarity />

                </div>
                <ToastContainer/>
            </>
        );
    }
}

const mapStateToProps = (state) => {
    return {
        nameContainer: state.nameContainer,
        auth: state.auth
    }
}

export default connect(mapStateToProps, null)(Similarity)