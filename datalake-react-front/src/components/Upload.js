import React from "react";
import { Header } from './Header';
import Dropzone from 'react-dropzone';
import { config } from '../configmeta/config';
import api from '../api/api';

export class Upload extends React.Component {
    constructor() {
        super();
        this.onDrop = (files) => {
            files.map((file) => { 
                const typeFile = file.type;
                const filename = file.name;
                var reader = new FileReader();
                reader.readAsDataURL(file);
                reader.onload = () => this.setState({file: reader.result});
                this.setState({typeFile: typeFile});
                this.setState({filename: filename});
                const f = [file]
                this.setState({files: f});
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
        };
        this.handleChange = this.handleChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
    }

    handleChange(event) {
        const target = event.target;
        const value = target.type === 'checkbox' ? target.checked : target.value;
        const name = target.name;

        this.setState({
        [name]: value
        });
    }
    
    handleSubmit(event) {
        event.preventDefault();
        const type = parseInt(this.state.type);
        if (this.state.type === 0) {
            window.alert("Veuillez renseigner le type de données !");
        } else if ( this.state.filename === ''){
            window.alert("Veuillez ajouter un fichier !");
        } else if (this.state.premieremeta === '') {
            window.alert("Veuillez renseigner la première metadonnée générique !");
        } else if (this.state.deuxiememeta === '') {
            window.alert("Veuillez renseigner la deuxième metadonnée générique !");
        } else {
            api.post('http://localhost/storage', {
                idType: type,
                typeFile: this.state.typeFile,
                filename: this.state.filename,
                file: this.state.file,
                premieremeta: this.state.premieremeta,
                deuxiememeta: this.state.deuxiememeta,
            })
            .then(function () {
                window.alert("L'upload a bien été fait")
                window.location.reload();
            })
            .catch(function (error) {
                window.alert("L'upload n'a pas réussi ! : " + error)
            });
        }
    }


    render() {
        const files = this.state.files.map(file => (
            <li key={file.name}>
                {JSON.stringify(file.name)}
            </li>
        ));

        const Metadonnees = () => {
            const types = [config.types];
            let listMeta = null;
            types.map((type) => (
                type.map((t) => {
                    if (t.id === parseInt(this.state.type)) {
                        listMeta = (
                            t.metadonnees.map((meta) => {
                                if(meta.type === "number" || meta.type === "text")
                                    return  <div class="mb-3">
                                                <label class="form-label">{meta.label}</label>
                                                <input type={meta.type} value={this.state.meta} onChange={this.handleChange} name="meta" class="form-control" />
                                            </div>
                                
                                if(meta.type === "textarea")
                                    return  <div class="mb-3">
                                                <label class="form-label">Métadonnée</label>
                                                <textarea value={this.state.meta} onChange={this.handleChange} name="meta" class="form-control" rows="3" />
                                            </div>
                                
                            })
                        );
                    }
                })
            ));
            return (
                <div>
                    {listMeta}
                </div>
                
            );
        }

        const SelectMetier = () => {
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
                            <div class="form-group">
                                <label>Type de données</label>
                                <SelectMetier />
                            </div>
                            {/* <div class="mb-3">
                                <label class="form-label">Métadonnée générique 1</label>
                                <input type="text" value={this.state.premieremeta} name="premieremeta" onChange={this.handleChange} class="form-control" />
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Métadonnée  générique 2</label>
                                <textarea value={this.state.deuxiememeta} onChange={this.handleChange} name="deuxiememeta" class="form-control" rows="3" />
                            </div> */}
                            <Metadonnees />
                            <div class="form-group">
                                <Dropzone value={this.state.file} name="file" onDrop={this.onDrop}>
                                    {({getRootProps, getInputProps}) => (
                                    <section>
                                        <div {...getRootProps({className: 'drop'})}>
                                            <input {...getInputProps()} />
                                            <p>Drag 'n' drop veuillez glisser un fichier ou cliquer pour ajouter un fichier.</p>
                                        </div>
                                        <aside class="pt-3">
                                            <h5>Files</h5>
                                            <ul>{files}</ul>
                                        </aside>
                                    </section>
                                    )}
                                </Dropzone>
                            </div>
                            <br />
                            <button type="submit" class="btn btn-primary">Submit</button>
                        </form>
                    </div>
                </div>
            </div>
        );
    }
}