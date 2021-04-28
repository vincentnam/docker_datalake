import React from "react";
import { Header } from './Header';
import Dropzone from 'react-dropzone';
import { config } from '../configmeta/config';

export class Upload extends React.Component {
    constructor() {
        super();
        this.onDrop = (files) => {
            this.setState({files})
        };
        this.state = {
            files: [],
            meta: '',
            type: 0,
            data: [],
            file: [],
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
        alert(this.state.type +' '+ this.state.meta + ' '+ JSON.stringify(this.state.files));
        event.preventDefault();
    }

    

    render() {
        const files = this.state.files.map(file => (
            <li key={file.name}>
                {JSON.stringify(file)}
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

        const Metadonnees = () => {
            const types = [config.types];
            let listMeta = null;
            types.map((type) => (
                type.map((t) => {
                    if (t.id === this.state.type) {
                        listMeta = t.metadonnees.map((meta) => {
                            if(meta.type === "number" || meta.type === "text"){
                                <div class="mb-3">
                                    <label class="form-label">{meta.label}</label>
                                    <input type={meta.type} value={this.state.meta} onChange={this.handleChange} name="meta" class="form-control" />
                                </div>
                            }
                            if(meta.type === "textarea"){
                                <div class="mb-3">
                                    <label class="form-label">Métadonnée</label>
                                    <textarea value={this.state.meta} onChange={this.handleChange} name="meta" class="form-control" rows="3" />
                                </div>
                            }
                        });
                    }
                })
            ));
            return (
                <div>
                    {listMeta}
                </div>
                
            );
        }


        return(
            <div>
                <Header />
                <div class="p-4">
                    <h4>Stockage de données</h4>
                    <form onSubmit={this.handleSubmit}>
                        <div class="form-group">
                            <label>Type de métadonnée</label>
                            <SelectMetier />
                        </div>
                        <Metadonnees />
                        <div class="form-group">
                            <Dropzone value={this.state.file} onChange={this.handleChange} name="file" onDrop={this.onDrop}>
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