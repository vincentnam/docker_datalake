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
        api.post('http://localhost/storage', {
            idType: type,
            typeFile: this.state.typeFile,
            filename: this.state.filename,
            file: this.state.file,
            premieremeta: this.state.premieremeta,
            deuxiememeta: this.state.deuxiememeta,
        })
        .then(function (response) {
            console.log(response);
        })
        .catch(function (error) {
            console.log(error);
        });
    }


    render() {
        const files = this.state.files.map(file => (
            <li key={file.name}>
                {JSON.stringify(file.name)}
            </li>
        ));

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
                    <h4>Stockage de données</h4>
                    <form onSubmit={this.handleSubmit}>
                        <div class="form-group">
                            <label>Type de données</label>
                            <SelectMetier />
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Métadonnée générique 1</label>
                            <input type="text" value={this.state.premieremeta} name="premieremeta" onChange={this.handleChange} class="form-control" />
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Métadonnée  générique 2</label>
                            <textarea value={this.state.deuxiememeta} onChange={this.handleChange} name="deuxiememeta" class="form-control" rows="3" />
                        </div>
                        <div class="form-group">
                            <Dropzone value={this.state.file} name="file" onDrop={this.onDrop}>
                                {({getRootProps, getInputProps}) => (
                                <section>
                                    <div {...getRootProps({className: 'drop d-flex justify-content-center'})}>
                                        <input {...getInputProps()} />
                                        <p>Drag 'n' drop veuillez glisser un fichier ou click pour ajouter un fichier.</p>
                                    </div>
                                    <aside>
                                        <h5>Files</h5>
                                        <ul>{files}</ul>
                                    </aside>
                                </section>
                                )}
                            </Dropzone>
                        </div>
                        <button type="submit" class="btn btn-primary">Submit</button>
                    </form>
                </div>
            </div>
        );
    }
}