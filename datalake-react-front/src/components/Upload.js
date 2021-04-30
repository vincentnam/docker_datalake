import React from "react";
import { Header } from './Header';
import Dropzone from 'react-dropzone';
import { config } from '../configmeta/config';
// import api from '../api/api';

export class Upload extends React.Component {
    constructor() {
        super();
        this.onDrop = (files) => {
            const f = [];
            files.map((file) => { 
                    var reader = new FileReader();
                    const typeFile = file.name.slice(file.name.lastIndexOf('.') + 1);
                    if (typeFile === "json") {
                        console.log('json');
                        // à faire
                    }
                    if (typeFile === "csv") {
                        console.log('csv');
                        var obj_csv = {
                            size:0,
                            dataFile:[]
                        };
                        reader.readAsBinaryString(file);
                        reader.onload = function (e) {
                            console.log(e);
                            obj_csv.size = e.total;
                            obj_csv.dataFile = e.target.result;
                            const data = obj_csv.dataFile;
                            let csvData = [];
                            let lbreak = data.split("\n");
                            lbreak.forEach(res => {
                                csvData.push(res.split(","));
                            });
                            let newData = {
                                "type": typeFile,
                                "data": csvData
                            }
                            f.push(newData);
                            console.log(newData);
                        }
                    }
                    if (typeFile === "xlsx") {
                        console.log('excel');
                        // à faire
                    }
                    if (typeFile === "sql") {
                        console.log('sql');
                        reader.readAsBinaryString(file);
                        reader.onload = function(e) {
                            var contents = e.target.result;
                            var res = contents.split("\n");
                            let data = {
                                "type": typeFile,
                                "data": res
                            }
                            f.push(data);
                            console.log(contents);
                        };
                        reader.readAsText(file);
                    }
                    if (typeFile === "png" || typeFile === 'PNG') {
                        console.log('png');
                        reader.onload = function(e) {
                            var contents = e.target.result;
                            let result = contents.slice(contents.lastIndexOf(',') + 1);
                            let data = {
                                "type": typeFile,
                                "data": result
                            }
                            f.push(data);
                            console.log(data);
                        };
                        reader.readAsDataURL(file);
                    }
                    if (typeFile === "txt") {
                        console.log('txt');
                        reader.onload = function(e) {
                            var contents = e.target.result;
                            var res = contents.split("\n");
                            let data = {
                                "type": typeFile,
                                "data": res
                            }
                            f.push(data);
                            console.log(data);
                        };
                        reader.readAsText(file);
                    }
                    
            });
            this.setState({files: f});
        };
        this.state = {
            files: [],
            meta: '',
            type: 0,
            data: [],
            file: [],
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
        alert(this.state.type +' '+ this.state.premieremeta +' '+ this.state.deuxiememeta + ' '+ JSON.stringify(this.state.files));
        event.preventDefault();
        // const type = parseInt(this.state.type);
        // api.post('/storage', {
        //     idType: this.state.type,
        //     data: this.state.files,
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
                        <div class="mb-3">
                            <label class="form-label">Métadonnée générique 1</label>
                            <input type="text" value={this.state.premieremeta} name="premieremeta" onChange={this.handleChange} class="form-control" />
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Métadonnée</label>
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