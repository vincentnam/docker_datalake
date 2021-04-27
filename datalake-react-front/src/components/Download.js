import React from 'react';
import { Header } from './Header';
import Dropzone from 'react-dropzone';

export class Download extends React.Component {
    constructor() {
        super();
        this.onDrop = (files) => {
            this.setState({files})
        };
        this.state = {
            files: [],
            meta: '',
            metier: 'meteo',
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
        alert(this.state.metier +' '+ this.state.meta + ' '+ JSON.stringify(this.state.files));
        event.preventDefault();
    }

    render() {
        const files = this.state.files.map(file => (
            <li key={file.name}>
                {JSON.stringify(file)}
            </li>
        ));

        return(
            <div>
                <Header />
                <div class="p-4">
                    <h4>Stockage de données</h4>
                    <form onSubmit={this.handleSubmit}>
                        <div class="form-group">
                            <label>Type de métadonnée</label>
                            <select value={this.state.metier} onChange={this.handleChange} name="metier" class="form-control">
                                <option value="meteo">Météo</option>
                                <option value="capteur">Capteur</option>
                                <option selected value="camera">Camera</option>
                            </select>
                        </div>
                        
                        <div class="mb-3">
                            <label class="form-label">Métadonnée</label>
                            <textarea value={this.state.meta} onChange={this.handleChange} name="meta" class="form-control" rows="3" />
                        </div>
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