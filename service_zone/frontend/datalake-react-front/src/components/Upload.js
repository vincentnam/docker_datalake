import React from "react";
import Dropzone from 'react-dropzone';
import { InputMeta } from './upload-child/InputMeta';
import { TextAreaMeta } from './upload-child/TextAreaMeta';
import { config } from '../configmeta/config';
import {configWithSGE} from "../configmeta/configWithSGE";
import { extensions_types_files } from '../configmeta/extensions_types_files';
import api from '../api/api';
import { ProgressBarComponent } from "./upload-child/ProgressBarComponent";
import filesize from "filesize";
import { ToastContainer, toast } from 'react-toastify';
import ModelAddForm from './upload-child/model/ModelAddForm';
import ModelEditForm from './upload-child/model/ModelEditForm';
import { Modal } from "react-bootstrap";
import {connect} from "react-redux";

class Upload extends React.Component {
    constructor() {
        super();
        this.onDrop = (files) => {
            if (files.length < 1) {
                toast.error('Format de fichier non accepté ou trop grand !', {
                    theme: "colored",
                    position: "top-right",
                    autoClose: 5000,
                    hideProgressBar: false,
                    closeOnClick: true,
                    pauseOnHover: true,
                    draggable: true,
                    progress: undefined,
                });
            }
            files.forEach((file) => {
                let typeFile = file.type;
                const filename = file.name;
                if (!typeFile && filename.split('.').pop().toLowerCase() === "sql") {
                    typeFile = "application/sql"
                }
                if (this.state.type_file_accepted.includes(typeFile) === false) {
                    toast.error("Format de fichier non accepté. Veuillez ajouter un fichier qui correspond à un de ses types : " + this.state.type_file_accepted.join(' '), {
                        theme: "colored",
                        position: "top-right",
                        autoClose: 5000,
                        hideProgressBar: false,
                        closeOnClick: true,
                        pauseOnHover: true,
                        draggable: true,
                        progress: undefined,
                    });
                } else {
                    var reader = new FileReader();
                    reader.readAsDataURL(file);
                    reader.onload = () => this.setState({ file: reader.result });
                    this.setState({ typeFile: typeFile });
                    this.setState({ filename: filename });
                    const f = [file]
                    this.setState({ files: f });
                }
            });
        };
        this.state = {
            files: [],
            meta: '',
            typeFile: '',
            filename: '',
            type: 0,
            data: [],
            file: '',
            premieremeta: '',
            deuxiememeta: '',
            othermeta: [],
            type_file_accepted: [],
            loading: false,
            percentProgressBar: 0,
            textProgressBar: '',
            linkFile: "",
            uploadLink: true,
            models: [],
            model: "",
            modalAdd: false,
            modalEdit: false,
            editModel: {
                id: 0,
                label: "",
                typesFiles: [],
                metadonnees: [],
                status: true,
            }
        };
        this.handleChange = this.handleChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
        this.changeType = this.changeType.bind(this);
        this.removeSelectedFile = this.removeSelectedFile.bind(this);
        this.onChangeModalAdd = this.onChangeModalAdd.bind(this);
        this.onChangeModalEdit = this.onChangeModalEdit.bind(this);
        this.reload = this.reload.bind(this);
        this.reloadEdit = this.reloadEdit.bind(this);
    }

    reload() {
        this.setState({
            model: "",
            type: 0,
            models: [],
            othermeta: [],
        });
    }

    reloadEdit() {
        this.setState({
            model: "",
            models: [],
            othermeta: [],
        });
        api.post("models/params", {
            types_files: this.state.type_file_accepted,
            container_name: this.props.nameContainer.nameContainer
        })
            .then((response) => {
                this.setState({
                    models: response.data.models.data,
                    model: "",
                    othermeta: [],
                    editModel: {
                        id: 0,
                        label: "",
                        typesFiles: [],
                        metadonnees: [],
                        status: true,
                    }
                });
            })
            .catch(function (error) {
                console.log(error);
            });
    }

    onChangeModalAdd() {
        this.setState({
            modalAdd: !this.state.modalAdd,
        });
    }

    onChangeModalEdit() {
        this.setState({
            modalEdit: !this.state.modalEdit,
        });
    }

    handleClose() {
        this.setState({
            loading: false
        })
    }

    handleShow() {
        this.setState({
            loading: true
        })
    }

    changeType(event) {
        const target = event.target;
        const value = target.type === 'checkbox' ? target.checked : target.value;
        const name = target.name;

        let type_file_accepted = [];
        if (name === "type") {
            if (value === "9") {
                this.setState({
                    type: value,
                    uploadLink: false,
                });
            } else {
                this.setState({
                    type: value,
                    uploadLink: true,
                });
            }
            let types = [];
            if(this.props.nameContainer.nameContainer === "neOCampus") {
                types = [configWithSGE.types];
            } else {
                types = [config.types];
            }
            types.forEach((type) => (
                type.forEach((t, key) => {
                    if (key === parseInt(value)) {
                        this.setState({
                            type_file_accepted: t.type_file_accepted
                        });
                        type_file_accepted = t.type_file_accepted
                        api.post("models/params", {
                            types_files: type_file_accepted,
                            container_name: this.props.nameContainer.nameContainer
                        })
                            .then((response) => {
                                this.setState({
                                    models: response.data.models.data,
                                    model: "",
                                    othermeta: [],
                                    editModel: {
                                        id: 0,
                                        label: "",
                                        typesFiles: [],
                                        metadonnees: [],
                                    }
                                });
                            })
                            .catch(function (error) {
                                console.log(error);
                            });
                    }
                })
            ));
        }
        if (this.state.typeFile !== "") {
            if (type_file_accepted.includes(this.state.typeFile) === false) {
                toast.error("Format de fichier non accepté. Veuillez ajouter un fichier qui correspond à un de ses types : " + type_file_accepted.join(' '), {
                    theme: "colored",
                    position: "top-right",
                    autoClose: 5000,
                    hideProgressBar: false,
                    closeOnClick: true,
                    pauseOnHover: true,
                    draggable: true,
                    progress: undefined,
                });
                this.removeSelectedFile()
            }
        }
    }


    handleChange(event) {
        const target = event.target;
        const value = target.type === 'checkbox' ? target.checked : target.value;
        const name = target.name;

        this.setState({
            [name]: value
        });
        if (name === "model") {
            if (value !== "") {
                api.post("models/id", {
                    id: value
                })
                    .then((response) => {
                        this.setState({
                            othermeta: response.data.model.metadonnees,
                            editModel: {
                                id: response.data.model._id,
                                label: response.data.model.label,
                                typesFiles: response.data.model.type_file_accepted,
                                metadonnees: response.data.model.metadonnees,
                                status: response.data.model.status,
                            }
                        });
                    })
                    .catch(function (error) {
                        console.log(error);
                    });
            } else {
                this.setState({
                    othermeta: [],
                    editModel: {
                        id: 0,
                        label: "",
                        typesFiles: [],
                        metadonnees: [],
                        status: true,
                    }
                });
            }
        }
    }

    handleSubmit(event) {
        event.preventDefault();
        const type = parseInt(this.state.type);
        const other = {};

        let type_link = "";
        let type_file = "";

        // options about upload progressBar
        const options = {
            onUploadProgress: (progressEvent) => {
                this.setState({ textProgressBar: "Envoi en cours..." })
                const { loaded, total } = progressEvent;
                let percent = Math.floor((loaded * 100) / total)
                this.setState({ percentProgressBar: percent })

                if (percent > 99) {
                    this.setState({ textProgressBar: "Finalisation du traitement..." })
                }
            }
        }

        this.state.othermeta.forEach((meta) => {
            other[meta.name] = meta.value
        });
        let nbErrors = 0;

        if (this.state.type === 0) {
            toast.error("Veuillez renseigner le type de données !", {
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

        if (this.state.filename === '' && this.state.linkFile.trim() === '') {
            toast.error("Veuillez ajouter un fichier ou un lien pour un fichier !", {
                theme: "colored",
                position: "top-right",
                autoClose: 5000,
                hideProgressBar: false,
                closeOnClick: true,
                pauseOnHover: true,
                draggable: true,
                progress: undefined,
            });
        } else {
            if (this.state.filename !== '' && this.state.linkFile.trim() !== '') {
                toast.error("Veuillez choisir entre ajouter un fichier, un lien http ou une ip pour ajouter un fichier !", {
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
            } else {
                if (this.state.linkFile.trim() !== '' && this.state.filename === '') {
                    // Check if HTTP or HTTPS in link
                    let check_http = false
                    let str_http = this.state.linkFile.trim().split("/");
                    if (str_http[0] === "https:") {
                        check_http = true;
                    }
                    if (str_http[0] === "http:") {
                        check_http = true;
                    }
                    if (check_http === true) {
                        type_link = "http";
                        let link = this.state.linkFile.trim().split(".");
                        // Check extension if is the same with choose in select type file
                        let extension = link[link.length - 1];
                        let content_type = "";
                        extensions_types_files.forEach(type => {
                            if (type.value === extension) {
                                content_type = type.content_type;
                            }
                        });
                        if (content_type === "") {
                            content_type = "application/octet-stream";
                        }
                        type_file = content_type;
                        if (this.state.type_file_accepted.includes(content_type) === false) {
                            toast.error("Le type de fichier dans le lien n'est pas identique au type sélectionné !", {
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

                        // Check if is a web site is compliant
                        let pattern = new RegExp('^(https?:\\/\\/)?' + // protocol
                            '((([a-z\\d]([a-z\\d-]*[a-z\\d])*)\\.)+[a-z]{2,}|' + // domain name
                            '((\\d{1,3}\\.){3}\\d{1,3}))' + // OR ip (v4) address
                            '(\\:\\d+)?(\\/[-a-z\\d%_.~+]*)*' + // port and path
                            '(\\?[;&a-z\\d%_.~+=-]*)?' + // query string
                            '(\\#[-a-z\\d_]*)?$', 'i');

                        if (!pattern.test(this.state.linkFile.trim())) {
                            toast.error("Le lien du fichier n'est pas pas un lien conforme !", {
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
                        //Search the domain site .com, .fr, .gouv et etc
                        let link_check = this.state.linkFile.trim().split('.');
                        let extension_domain_link = link_check[1].split('/');
                        extension_domain_link = extension_domain_link[0];
                        let domain_check = false;
                        extensions_types_files.forEach(type => {
                            if (type.value === extension_domain_link) {
                                domain_check = true;
                            }
                        });

                        if (domain_check === true) {
                            toast.error("Le lien du fichier n'est pas pas un lien conforme !", {
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
                    } else {
                        type_link = "ip";
                        let link = this.state.linkFile.trim().split("/");
                        // Check extension if is the same with choose in select type file
                        let extension = link[link.length - 1].split(".");
                        extension = extension[1];
                        let content_type = "";
                        extensions_types_files.forEach(type => {
                            if (type.value === extension) {
                                content_type = type.content_type;
                            }
                        });
                        if (content_type === "") {
                            content_type = "application/octet-stream";
                        }
                        type_file = content_type;
                        if (this.state.type_file_accepted.includes(content_type) === false) {
                            toast.error("Le type de fichier dans le lien n'est pas identique au type sélectionné !", {
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
                        //Check IP adress is compliant
                        let ipformat = /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
                        let iplink = link[0];
                        if (!ipformat.test(iplink)) {
                            toast.error("L'adresse IP n'est pas conforme !", {
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
                    }
                }
            }
        }
        if (nbErrors === 0) {
            let typeFile = this.state.typeFile;
            if (this.state.linkFile.trim() !== "") {
                typeFile = type_file;
            }
            this.handleShow()
            api.post('storage', {
                idType: type,
                typeFile: typeFile,
                filename: this.state.filename,
                file: this.state.file,
                linkFile: this.state.linkFile.trim(),
                linkType: type_link,
                othermeta: other,
                container_name: this.props.nameContainer.nameContainer
            }, options)
                .then(function () {
                    toast.success("L'upload a bien été fait !", {
                        theme: "colored",
                        position: "top-right",
                        autoClose: 1500,
                        hideProgressBar: false,
                        closeOnClick: true,
                        pauseOnHover: false,
                        draggable: true,
                        progress: undefined,
                    });
                    setTimeout(function () { window.location.reload() }, 1500);
                })
                .catch(function (error) {
                    toast.error("L'upload n'a pas réussi ! : " + error, {
                        theme: "colored",
                        position: "top-right",
                        autoClose: 4000,
                        hideProgressBar: false,
                        closeOnClick: true,
                        pauseOnHover: true,
                        draggable: true,
                        progress: undefined,
                    });
                }).finally(function () {
                    this.handleClose()
                }.bind(this))
        }
    }

    // remove selected file on upload page
    removeSelectedFile() {
        this.setState({ file: '' });
        this.setState({ typeFile: '' });
        this.setState({ filename: '' });
        this.setState({ files: [] });
    }

    render() {

        const files = this.state.files.map(file => (
            <li key={file.name}>
                {file.name} <span className="filesize">{filesize(file.size)}</span>
                <div className="supprimer" onClick={this.removeSelectedFile}>
                    <span aria-hidden="true">Supprimer</span><img alt="Icon Trash" src="/images/trash.svg" />
                </div>
            </li>
        ));

        const Metadonnees = () => {
            let listMeta = null;
            let othermeta = this.state.othermeta;
            listMeta = (
                othermeta.map((meta) => {
                    const index = othermeta.indexOf(meta);
                    if (meta.type === "number" || meta.type === "text")
                        return <InputMeta key={meta.name} meta={meta} othermeta={othermeta} index={index} />

                    if (meta.type === "textarea")
                        return <TextAreaMeta key={meta.name} meta={meta} othermeta={othermeta} index={index} />
                })
            );
            return (
                <div className="row">
                    {listMeta}
                </div>

            );
        }
        const SelectDatatype = () => {
            let types = [];
            if(this.props.nameContainer.nameContainer === "neOCampus") {
                types = [configWithSGE.types];
            } else {
                types = [config.types];
            }


            const listTypes = types.map((type) => (
                type.map((t, key) =>
                    <option value={key}>{t.label}</option>
                )
            ));
            return (
                <select value={this.state.type} onChange={this.changeType} name="type" className="form-select">
                    {listTypes}
                </select>
            );
        }

        const SelectModel = () => {
            if (this.state.models.length === 0) {
                return (
                    <div>
                        <p className="text-break">Aucun modèle de métadonnées</p>
                    </div>
                );
            } else {
                const listModels = this.state.models.map((model) => (
                    <option key={model._id} value={model._id}>{model.label}</option>
                ));
                return (
                    <select value={this.state.model} onChange={this.handleChange} name="model" className="form-select">
                        <option value="">Sélectionnez un modèle de métadonnées</option>
                        {listModels}
                    </select>
                );
            }
        }

        const EditButton = () => {
            if (this.state.model !== "") {
                return (
                    <button type="button" className="btn btn-primary buttonModel" onClick={() => this.onChangeModalEdit()}>Modifier le modèle</button>
                );
            } else {
                return (
                    <p></p>
                )
            }
        }

        const ModalAdd = () => {
            return (
                <Modal
                    size="lg"
                    show={this.state.modalAdd}
                    onHide={() => this.onChangeModalAdd()}
                    aria-labelledby="model-add"
                >
                    <Modal.Header>
                        <Modal.Title id="model-add">
                            Ajouter un modèle de métadonnées
                        </Modal.Title>
                    </Modal.Header>
                    <Modal.Body>
                        <ModelAddForm
                            close={this.onChangeModalAdd}
                            reload={this.reload}
                        />
                    </Modal.Body>
                </Modal>
            )
        }
        const ModalEdit = () => {
            return (
                <Modal
                    size="lg"
                    show={this.state.modalEdit}
                    onHide={() => this.onChangeModalEdit()}
                    aria-labelledby="model-edit"
                >
                    <Modal.Header>
                        <Modal.Title id="model-edit">
                            Modifier le modèle
                        </Modal.Title>
                    </Modal.Header>
                    <Modal.Body>
                        <ModelEditForm
                            close={this.onChangeModalEdit}
                            reload={this.reloadEdit}
                            editModel={this.state.editModel}
                        />
                    </Modal.Body>
                </Modal>
            )
        }

        return (
            <div>
                <div className="container main-upload">
                    <div className="title">Upload de données</div>
                    <div className="jumbotron">
                        <form onSubmit={this.handleSubmit}>
                            <div className="row">
                                <div className="form-group required col-6">
                                    <label className="control-label file-type">Type de fichier</label>
                                    <SelectDatatype />
                                </div>
                                <div className="form-group required col-6">
                                    <label className="control-label file-type">Modèles</label>
                                    <SelectModel />
                                </div>
                            </div>
                            <Metadonnees />
                            <div className="d-flex justify-content-between mt-2 mb-2">
                                <button type="button" className="btn btn-primary buttonModel" onClick={() => this.onChangeModalAdd()}>Créer un modèle</button>
                                <EditButton />
                            </div>
                            {this.state.uploadLink === false &&
                                <div className="main-download mt-4 mb-5">
                                    <div className="form-group required">
                                        <label className="form-label">Lien vers le fichier</label>
                                        <input value={this.state.linkFile} onChange={this.handleChange} type="text" name="linkFile" className="form-control"
                                            placeholder="https://-----/dossier/file.extension ou XX.XX.XX.XXX/dossier/file.extension" />
                                    </div>
                                </div>
                            }
                            {this.state.uploadLink === true &&
                                <div className="main-download">
                                    <div className="main-download">
                                        <nav className="tab-download">
                                            <div className="nav nav-pills " id="pills-tab" role="tablist">
                                                <button className="nav-link active" id="nav-raw-tab" data-bs-toggle="pill"
                                                    data-bs-target="#nav-small-file" type="button" role="tab" aria-controls="nav-small-file"
                                                    aria-selected="true">Fichier moins de 250 Mo
                                                </button>
                                                <button className="nav-link" id="nav-handled-tab" data-bs-toggle="pill"
                                                    data-bs-target="#nav-large-file" type="button" role="tab" aria-controls="nav-large-file"
                                                    aria-selected="false">Fichier plus de 250 Mo
                                                </button>
                                            </div>
                                        </nav>
                                        <div className="tab-content" id="pills-tabContent">
                                            <div className="tab-pane fade show active" id="nav-small-file" role="tabpanel"
                                                aria-labelledby="nav-small-file-tab">
                                                <div className="form-group required">
                                                    <label>Fichiers</label>
                                                    <Dropzone value={this.state.file} name="file" onDrop={this.onDrop} maxSize={250000000}
                                                        accept="image/*,application/JSON,.csv,text/plain,.sql,application/x-gzip,application/x-zip-compressed,application/octet-stream">
                                                        {({ getRootProps, getInputProps }) => (
                                                            <section>
                                                                <div {...getRootProps({ className: 'drop' })}>
                                                                    <input {...getInputProps()} />
                                                                    <div>
                                                                        Veuillez glisser un fichier ici<br />
                                                                        ou<br />
                                                                        <u>cliquer pour ajouter un fichier</u><br />
                                                                        Taille limitée à 250Mo (.jpg, .jpeg, .png, .svg, .csv, .json, .zip, .sql et .txt)
                                                                    </div>
                                                                </div>
                                                                <aside className="pt-3">
                                                                    {files.length !== 0 ?
                                                                        <aside className="pt-3">
                                                                            <ul>
                                                                                {files}
                                                                            </ul>
                                                                        </aside>
                                                                        : ''}
                                                                </aside>
                                                            </section>
                                                        )}
                                                    </Dropzone>
                                                </div>
                                            </div>
                                            <div className="tab-pane fade mb-4" id="nav-large-file" role="tabpanel"
                                                aria-labelledby="nav-large-file-tab">
                                                <div className="form-group required">
                                                    <label className="form-label">Lien vers le fichier</label>
                                                    <input value={this.state.linkFile} onChange={this.handleChange} type="text" name="linkFile" className="form-control"
                                                        placeholder="https://-----/dossier/file.extension ou XX.XX.XX.XXX/dossier/file.extension" />
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            }

                            <div className="d-md-flex justify-content-center">
                                <button type="submit" className="btn btn-oran">Upload le fichier</button>
                            </div>
                        </form>
                    </div>
                    <ModalAdd />
                    <ModalEdit />
                </div>

                {/* ProgressBar shown when upload form submitted with percent updated in onUploadProgress above */}
                <ProgressBarComponent
                    loading={this.state.loading}
                    percentProgressBar={this.state.percentProgressBar}
                    text={this.state.textProgressBar}
                />
                <ToastContainer />
            </div>
        );
    }
}

const mapStateToProps = (state) => {
    return {
        nameContainer: state.nameContainer,
    }
}

export default connect(mapStateToProps, null)(Upload)