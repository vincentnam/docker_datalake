import React from "react";
import { Header } from './Header';
import Dropzone from 'react-dropzone';
import { InputMeta } from './upload-child/InputMeta';
import { TextAreaMeta } from './upload-child/TextAreaMeta';
import { config } from '../configmeta/config';
import api from '../api/api';
import { ProgressBarComponent } from "./upload-child/ProgressBarComponent";
import filesize from "filesize";
import { ToastContainer, toast } from 'react-toastify';
import { ModelAddForm } from './upload-child/model/ModelAddForm';
import { ModelEditForm } from './upload-child/model/ModelEditForm';
import { Modal, Button } from "react-bootstrap";

export class Upload extends React.Component {
    constructor() {
        super();
        this.onDrop = (files) => {
            if (files.length < 1) {
                toast.error('Format de fichier non accepté.', {
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
            types_files: this.state.type_file_accepted
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

    handleChange(event) {
        const target = event.target;
        const value = target.type === 'checkbox' ? target.checked : target.value;
        const name = target.name;

        this.setState({
            [name]: value
        });
        let type_file_accepted = [];
        if (name === "type") {
            const types = [config.types];
            types.forEach((type) => (
                type.forEach((t) => {
                    if (t.id === parseInt(value)) {
                        this.setState({
                            type_file_accepted: t.type_file_accepted
                        });
                        type_file_accepted = t.type_file_accepted
                        api.post("models/params", {
                            types_files: type_file_accepted
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
                })
            ));
        }
        if (name === "model") {
            api.post("models/id", {
                id: value
            })
                .then((response) => {
                    this.setState({
                        othermeta: response.data.model.data[0].metadonnees,
                        editModel: {
                            id: response.data.model.data[0]._id,
                            label: response.data.model.data[0].label,
                            typesFiles: response.data.model.data[0].type_file_accepted,
                            metadonnees: response.data.model.data[0].metadonnees,
                            status: response.data.model.data[0].status,
                        }
                    });
                })
                .catch(function (error) {
                    console.log(error);
                });
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

    handleSubmit(event) {
        event.preventDefault();
        const type = parseInt(this.state.type);
        const other = {};

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
        } else if (this.state.filename === '') {
            toast.error("Veuillez ajouter un fichier !", {
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
            this.handleShow()
            api.post('storage', {
                idType: type,
                typeFile: this.state.typeFile,
                filename: this.state.filename,
                file: this.state.file,
                othermeta: other
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
            const othermeta = this.state.othermeta;
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
            const types = [config.types];
            const listTypes = types.map((type) => (
                type.map((t) =>
                    <option value={t.id}>{t.label}</option>
                )
            ));
            return (
                <select value={this.state.type} onChange={this.handleChange} name="type" class="form-select">
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
                    <select value={this.state.model} onChange={this.handleChange} name="model" class="form-select">
                        <option value="">Sélectionnez un modèle de métadonnées</option>
                        {listModels}
                    </select>
                );
            }
        }

        const EditButton = () => {
            if (this.state.model !== "") {
                return (
                    <button type="button" class="btn btn-primary buttonModel" onClick={() => this.onChangeModalEdit()}>Modifier le modèle</button>
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
                <Header />
                <div class="container main-upload">
                    <div className="title">Upload de données</div>
                    <div class="jumbotron">
                        <form onSubmit={this.handleSubmit}>
                            <div className="row">
                                <div class="form-group required col-6">
                                    <label class="control-label file-type">Type de fichier</label>
                                    <SelectDatatype />
                                </div>
                                <div class="form-group required col-6">
                                    <label class="control-label file-type">Modèles</label>
                                    <SelectModel />
                                </div>
                            </div>
                            <Metadonnees />
                            <div class="d-flex justify-content-between mt-2 mb-2">
                                <button type="button" class="btn btn-primary buttonModel" onClick={() => this.onChangeModalAdd()}>Créer un modèle</button>
                                <EditButton />
                            </div>
                            <div class="form-group required">
                                <label>Fichiers</label>
                                <Dropzone value={this.state.file} name="file" onDrop={this.onDrop}
                                    accept="image/*,application/JSON,.csv,text/plain,.sql,application/x-gzip,application/x-zip-compressed">
                                    {({ getRootProps, getInputProps }) => (
                                        <section>
                                            <div {...getRootProps({ className: 'drop' })}>
                                                <input {...getInputProps()} />
                                                <div>
                                                    Veuillez glisser un fichier ici<br />
                                                    ou<br />
                                                    <u>cliquer pour ajouter un fichier</u><br />
                                                    Taille limitée à 20Mo (.jpg, .jpeg, .png, .svg, .gif, .tif, .psd,
                                                    .pdf, .eps, .ai, .indd, .svg)
                                                </div>
                                            </div>
                                            <aside class="pt-3">
                                                {files.length !== 0 ?
                                                    <aside class="pt-3">
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