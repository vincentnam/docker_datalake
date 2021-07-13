<<<<<<< HEAD
import React from "react";
import { Header } from './Header';
import Dropzone from 'react-dropzone';
import { InputMeta } from './upload-child/InputMeta';
import { TextAreaMeta } from './upload-child/TextAreaMeta';
import { config } from '../configmeta/config';
import api from '../api/api';
import { ProgressBarComponent } from "./upload-child/ProgressBarComponent";
import { ProgressBar } from "react-bootstrap"

export class Upload extends React.Component {
    constructor() {
        super();
        this.onDrop = (files) => {
            if (files.length < 1) {
                alert('Format de fichier non accepté.')
            }
            files.map((file) => {
                const typeFile = file.type;
                const filename = file.name;
                if (this.state.type_file_accepted.includes(typeFile) === false) {
                    alert("Format de fichier non accepté.\nVeuillez ajouter un fichier qui correspond à un de ses types : \n" + this.state.type_file_accepted)
                } else {
                    var reader = new FileReader();
                    reader.readAsDataURL(file);
                    reader.onload = () => this.setState({ file: reader.result });
                    this.setState({ typeFile: typeFile });
                    this.setState({ filename: filename });
                    const f = [file];
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
                this.setState({ textProgressBar: "Envoi en cours..." })
                const { loaded, total } = progressEvent;
                let percent = Math.floor((loaded * 100) / total)
                this.setState({ percentProgressBar: percent })

                if (percent > 99) {
                    this.setState({ textProgressBar: "Finalisation du traitement..." })
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
                }).finally(function () { this.handleClose() }.bind(this))
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
                {JSON.stringify(file.name)}

                <button type="button" onClick={this.removeSelectedFile} class="close text-danger" aria-label="Close">
                    <span aria-hidden="true">&times;</span>
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
                        return <InputMeta key={meta.name} meta={meta} othermeta={othermeta} index={index} />

                    if (meta.type === "textarea")
                        return <TextAreaMeta key={meta.name} meta={meta} othermeta={othermeta} index={index} />
                })
            );
            return (
                <div>
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
                <Header />
                <div class="p-4">
                    <div class="jumbotron">
                        <h2 class="display-4 text-center">Upload de données</h2>
                        <form onSubmit={this.handleSubmit}>
                            <div class="form-group required">
                                <label class="control-label">Type de données</label>
                                <SelectDatatype />
                            </div>
                            <Metadonnees />
                            <div class="form-group required">
                                <Dropzone value={this.state.file} name="file" onDrop={this.onDrop} accept="image/*,application/JSON,.csv,text/plain,application/x-gzip,application/x-zip-compressed">
                                    {({ getRootProps, getInputProps }) => (
                                        <section>
                                            <div {...getRootProps({ className: 'drop' })}>
                                                <input {...getInputProps()} />
                                                <label class="control-label">Drag 'n' drop veuillez glisser un fichier ou cliquer pour ajouter un fichier.</label>
                                            </div>
                                            <aside class="pt-3">
                                                {files.length !== 0 ?
                                                    <aside class="pt-3">
                                                        <h5>Fichiers</h5>
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
                            <br />
                            <button type="submit" class="btn btn-primary">Upload</button>
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
=======
import React from "react";
import { Header } from './Header';
import Dropzone from 'react-dropzone';
import { InputMeta } from './upload-child/InputMeta';
import { TextAreaMeta } from './upload-child/TextAreaMeta';
import { config } from '../configmeta/config';
import api from '../api/api';
import { ProgressBarComponent } from "./upload-child/ProgressBarComponent";

export class Upload extends React.Component {
    constructor() {
        super();
        this.onDrop = (files) => {
            if(files.length < 1) {
                alert('Format de fichier non accepté.')
            } 
            files.map((file) => { 
                const typeFile = file.type;
                const filename = file.name;
                if(this.state.type_file_accepted.includes(typeFile) === false) {
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
        if(this.state.typeFile !== "") {
            if(type_file_accepted.includes(this.state.typeFile) === false) {
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
                let percent = Math.floor( (loaded * 100) / total )
                this.setState({percentProgressBar: percent})

                if(percent > 99) {
                    this.setState({textProgressBar: "Finalisation du traitement..."})
                }
            }
        }

        this.state.othermeta.map((meta) => {
            other[meta.name] = meta.value
        });

        if (this.state.type === 0) {
            window.alert("Veuillez renseigner le type de données !");
        } else if ( this.state.filename === ''){
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
            }).finally(function(){this.handleClose()}.bind(this))
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
                {JSON.stringify(file.name)}
                
                <button type="button" onClick={this.removeSelectedFile} class="close text-danger" aria-label="Close">
                    <span aria-hidden="true">&times;</span>
                </button>
            </li>
        ));

        const Metadonnees = () => {
            let listMeta = null;
            const othermeta = this.state.othermeta;
            listMeta = (
                othermeta.map((meta) => {
                    const index = othermeta.indexOf(meta)
                    if(meta.type === "number" || meta.type === "text") 
                        return  <InputMeta key={meta.name} meta={meta} othermeta={othermeta} index={index} />
    
                    if(meta.type === "textarea") 
                        return  <TextAreaMeta key={meta.name} meta={meta} othermeta={othermeta} index={index} />
                })
            );
            return (
                <div>
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

        return(
            <div>
                <Header />
                <div class="p-4">
                    <div class="jumbotron">
                        <h2 class="display-4 text-center">Upload de données</h2>
                        <form onSubmit={this.handleSubmit}>
                            <div class="form-group required">
                                <label class="control-label">Type de données</label>
                                <SelectDatatype />
                            </div>
                            <Metadonnees />
                            <div class="form-group required">
                                <Dropzone value={this.state.file} name="file" onDrop={this.onDrop} accept="image/*,application/JSON,.csv,text/plain">
                                    {({getRootProps, getInputProps}) => (
                                    <section>
                                        <div {...getRootProps({className: 'drop'})}>
                                            <input {...getInputProps()} />
                                            <label class="control-label">Drag 'n' drop veuillez glisser un fichier ou cliquer pour ajouter un fichier.</label>
                                        </div>
                                        <aside class="pt-3">
                                            { files.length !== 0 ? 
                                                <aside class="pt-3">
                                                    <h5>Fichiers</h5>
                                                    <ul>
                                                        {files}
                                                    </ul>
                                                </aside>
                                            : '' }
                                        </aside>
                                    </section>
                                    )}
                                </Dropzone>
                            </div>
                            <br />
                            <button type="submit" class="btn btn-primary">Upload</button>
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
>>>>>>> 1f3842d... #77 - added filters - resolved front errors/warnings from React
}