import React from 'react';
import { Header } from './Header';
import Dropzone  from 'react-dropzone';

export class Download extends React.Component {
    render() {
        return(
            <div>
                <Header />
                <div class="p-4">
                    <h4>Stockage de données</h4>
                    <form>
                        <div class="form-group">
                            <label for="inputState">Type de métadonnée</label>
                            <select id="inputState" class="form-control">
                                <option selected>Choose...</option>
                                <option>...</option>
                            </select>
                        </div>
                        
                        <div class="mb-3">
                            <label for="exampleFormControlTextarea1" class="form-label">Example textarea</label>
                            <textarea class="form-control" id="exampleFormControlTextarea1" rows="3"></textarea>
                        </div>
                        <div class="form-group">
                            <label for="exampleFormControlFile1">Example file input</label>
                            <Dropzone onDrop={acceptedFiles => console.log(acceptedFiles)}>
                                {({getRootProps, getInputProps}) => (
                                    <section>
                                    <div class="drop d-flex justify-content-center align-items-center" {...getRootProps()}>
                                        <input {...getInputProps()} />
                                        <p>Veuillez cliquer ou glisser votre fichier.</p>
                                    </div>
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