import React from "react";
import {Header} from './Header';
import Dropzone from 'react-dropzone';
import {InputMeta} from './upload-child/InputMeta';
import {TextAreaMeta} from './upload-child/TextAreaMeta';
import {config} from '../configmeta/config';
import api from '../api/api';
import {ProgressBarComponent} from "./upload-child/ProgressBarComponent";
import filesize from "filesize";

export class Upload extends React.Component {
    constructor() {
        super();
        this.onDrop = (files) => {
            if (files.length < 1) {
                alert('Format de fichier non accepté.')
            }
            files.map((file) => {
                let typeFile = file.type;
                const filename = file.name;
                if (!typeFile && filename.split('.').pop().toLowerCase() === "sql") {
                    typeFile = "application/sql"
                }
                if (this.state.type_file_accepted.includes(typeFile) === false) {
                    alert("Format de fichier non accepté.\nVeuillez ajouter un fichier qui correspond à un de ses types : \n" + this.state.type_file_accepted)
                } else {
                    var reader = new FileReader();
                    reader.readAsDataURL(file);
                    reader.onload = () => this.setState({file: reader.result});
                    this.setState({typeFile: typeFile});
                    this.setState({filename: filename});
                    const f = [file]
                    this.setState({files: f});
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
            textProgressBar: ''
        };
        this.handleChange = this.handleChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
        this.removeSelectedFile = this.removeSelectedFile.bind(this);
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
            types.map((type) => (
                type.map((t) => {
                    if (t.id === parseInt(value)) {
                        this.setState({
                            othermeta: t.metadonnees,
                            type_file_accepted: t.type_file_accepted
                        });
                        type_file_accepted = t.type_file_accepted
                    }
                })
            ));
        }
        if (this.state.typeFile !== "") {
            if (type_file_accepted.includes(this.state.typeFile) === false) {
                alert("Format de fichier non accepté.\nVeuillez ajouter un fichier qui correspond à un de ses types : \n" + type_file_accepted)
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
                this.setState({textProgressBar: "Envoi en cours..."})
                const {loaded, total} = progressEvent;
                let percent = Math.floor((loaded * 100) / total)
                this.setState({percentProgressBar: percent})

                if (percent > 99) {
                    this.setState({textProgressBar: "Finalisation du traitement..."})
                }
            }
        }

        this.state.othermeta.map((meta) => {
            other[meta.name] = meta.value
        });

        if (this.state.type === 0) {
            window.alert("Veuillez renseigner le type de données !");
        } else if (this.state.filename === '') {
            window.alert("Veuillez ajouter un fichier !");
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
                    window.alert("L'upload a bien été fait")
                    window.location.reload();
                })
                .catch(function (error) {
                    console.log(error);
                    window.alert("L'upload n'a pas réussi ! : " + error)
                }).finally(function () {
                this.handleClose()
            }.bind(this))
        }
    }

    // remove selected file on upload page
    removeSelectedFile() {
        this.setState({file: ''});
        this.setState({typeFile: ''});
        this.setState({filename: ''});
        this.setState({files: []});
    }

    render() {

        const files = this.state.files.map(file => (
            <li key={file.name}>
                {file.name} <span className="filesize">{filesize(file.size)}</span>

                <button type="button" onClick={this.removeSelectedFile} class="close text-danger" aria-label="Close">
                    <div className="supprimer"><span aria-hidden="true">Supprimer</span><img src="/images/trash.svg"/>
                    </div>
                </button>
            </li>
        ));

        const Metadonnees = () => {
            let listMeta = null;
            const othermeta = this.state.othermeta;
            listMeta = (
                othermeta.map((meta) => {
                    const index = othermeta.indexOf(meta)
                    if (meta.type === "number" || meta.type === "text")
                        return <InputMeta key={meta.name} meta={meta} othermeta={othermeta} index={index}/>

                    if (meta.type === "textarea")
                        return <TextAreaMeta key={meta.name} meta={meta} othermeta={othermeta} index={index}/>
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
                <select value={this.state.type} onChange={this.handleChange} name="type" class="form-control">
                    {listTypes}
                </select>
            );
        }

        return (
            <div>
                <Header/>
                <div class="container main-upload">
                    <div className="title">Upload de données</div>
                    <div class="jumbotron">
                        <form onSubmit={this.handleSubmit}>
                            <div className="row">
                                <div class="form-group required col-6">
                                    <label class="control-label file-type">Type de fichier</label>
                                    <SelectDatatype/>
                                </div>
                            </div>
                            <Metadonnees/>
                            <div class="form-group required">
                                <label>Fichiers</label>
                                <Dropzone value={this.state.file} name="file" onDrop={this.onDrop}
                                          accept="image/*,application/JSON,.csv,text/plain,.sql,application/x-gzip,application/x-zip-compressed">
                                    {({getRootProps, getInputProps}) => (
                                        <section>
                                            <div {...getRootProps({className: 'drop'})}>
                                                <input {...getInputProps()} />
                                                <div>
                                                    Veuillez glisser un fichier ici<br/>
                                                    ou<br/>
                                                    <u>cliquer pour ajouter un fichier</u><br/>
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
                            <div className="row justify-content-center">
                                <button type="submit" className="btn btn-oran">Upload le fichier</button>
                            </div>
                        </form>
                    </div>
                </div>

                {/* ProgressBar shown when upload form submitted with percent updated in onUploadProgress above */}
                <ProgressBarComponent
                    loading={this.state.loading}
                    percentProgressBar={this.state.percentProgressBar}
                    text={this.state.textProgressBar}
                />
            </div>
        );
    }
}