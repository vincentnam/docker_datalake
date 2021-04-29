import React from "react";
import { Header } from './Header';
import Dropzone from 'react-dropzone';
import { config } from '../configmeta/config';
// import api from '../api/api';

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
        const types = [config.types];
        types.map((type) => (
            type.map((t) => {
                if (t.id === parseInt(this.state.type)) {
                    t.metadonnees.map((meta) => {
                        let m = document.getElementById(meta.id).value;
                        console.log(m);
                    })
                }
            })
        ));
        const dataFiles = [];
        this.state.files.map((file) => {
            const typeFile = file.name.slice(file.name.lastIndexOf('.') + 1);
            let data = null;
            console.log(typeFile);
            if (typeFile === "csv") {
                console.log('csv');
            }
            if (typeFile === "excel") {
                console.log('excel');
            }
            if (typeFile === "sql") {
                console.log('sql');
            }
            if (typeFile === "png" || typeFile === 'PNG') {
                console.log('png');
            }
            if (typeFile === "txt") {
                console.log('txt');
                var rawFile = new XMLHttpRequest();
                rawFile.open("GET", `file://${file.name}`, false);
                rawFile.onreadystatechange = function ()
                {
                    if(rawFile.readyState === 4)
                    {
                        if(rawFile.status === 200 || rawFile.status === 0)
                        {
                            data = rawFile.responseText;
                        }
                    }
                }
                rawFile.send(null);
            }
            dataFiles.push(data);
        });
        console.log(dataFiles);
        alert(this.state.type +' '+ this.meta1 + ' '+ JSON.stringify());
        event.preventDefault();
        // const type = parseInt(this.state.type);
        // api.post('/storage', {
        //     idType: type,
        //     data: "dataFile",
        //     meta1: '',
        //     meta2: '',
        // })
        // .then(function (response) {
        //     console.log(response);
        // })
        // .catch(function (error) {
        //     console.log(error);
        // });
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

        const Metadonnees = () => {
            const types = [config.types];
            let listMeta = null;
            types.map((type) => (
                type.map((t) => {
                    if (t.id === parseInt(this.state.type)) {
                        listMeta = (
                            t.metadonnees.map((meta) => {
                                if(meta.type === "number" || meta.type === "text")
                                    return  <div key={meta.id} class="mb-3">
                                                <label class="form-label">{meta.label}</label>
                                                <input type={meta.type} id={meta.id} class="form-control" />
                                            </div>
                                
                                if(meta.type === "textarea")
                                    return  <div key={meta.id} class="mb-3">
                                                <label class="form-label">Métadonnée</label>
                                                <textarea id={meta.id} class="form-control" rows="3" />
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