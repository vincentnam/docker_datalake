import React from "react";
import api from '../../api/api';
import { FormGroup, FormLabel, Form, Button } from "react-bootstrap";
import Select from 'react-select';
import { types_files } from '../../configmeta/types_files';

export class ModelAddForm extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            models: [],
            model: {},
            newModel: {},
            typesFiles: types_files,
            selectedTypesFiles: null
        };
        this.handleChange = this.handleChange.bind(this);
        this.handleChangeType = this.handleChangeType.bind(this);
    }
    loadModel() {
        api.get('models')
            .then((response) => {
                this.setState({
                    models: response.data.models
                });
            })
            .catch(function (error) {
                console.log(error);
            });
    }

    submitModels() {
        api.post('models/add')
            .then((response) => {
                console.log(response)
            })
            .catch(function (error) {
                console.log(error);
            });
    }

    handleChangeType(event) {
        console.log(event);
        let types = [];
        event.forEach( type =>types.push(type.value) );
        const name = "selectedTypesFiles";
        this.setState({
            [name]: types,
        });
    }

    handleChange(event) {
        console.log(event);
        const target = event.target;
        const value = target.type === 'checkbox' ? target.checked : target.value;
        const name = target.name;

        this.setState({
            [name]: value,
        });
    }
    //handleCallbackData = (childData) =>{
    //    this.setState({dataFilters: childData})
    //}

    render() {
        const Metadonnees = () => {
            return (
                <div className="card col-sm-5 mt-2 mb-2 pb-2 pt-2">
                    <FormGroup>
                        <FormLabel>Label</FormLabel>
                        <Form.Control type="text" placeholder="Label de la métadonnée"></Form.Control>
                    </FormGroup>
                    <FormGroup>
                        <FormLabel>Type de champs</FormLabel>
                        <Form.Control as="select" aria-label="Label de la métadonnée">
                            <option>Veuillez choisir le type de champs</option>
                            <option value="text">Text</option>
                            <option value="number">Number</option>
                            <option value="textarea">Textareas</option>
                        </Form.Control>
                    </FormGroup>
                    <FormGroup>
                        <FormLabel>Name</FormLabel>
                        <Form.Control type="text" placeholder="Name de la métadonnée"></Form.Control>
                    </FormGroup>
                </div>
            );
        }



        return (
            <div className="col-sm-10 card pt-2 pb-2">
                <h5>Ajout d'un modèle de métadonnées</h5>
                <Form onSubmit={this.submitModels}>
                    <FormGroup>
                        <FormLabel>Label</FormLabel>
                        <Form.Control type="text" placeholder="Label du modèle"></Form.Control>
                    </FormGroup>
                    <FormGroup>
                        <FormLabel>Types de fichiers</FormLabel>
                        <Select
                            onChange={this.handleChangeType}
                            isMulti
                            name="typeFile"
                            className="basic-multi-select"
                            classNamePrefix="select"
                            options={this.state.typesFiles} />
                    </FormGroup>
                    <FormGroup className="mt-2">
                        <div>
                            <FormLabel>Métadonnées</FormLabel>
                            <button className="btn btn-primary btn-sm">Ajouter</button>
                        </div>
                        <div className="row d-flex justify-content-around col-sm-12">
                            <Metadonnees />
                            <Metadonnees />
                            <Metadonnees />
                            <Metadonnees />
                            <Metadonnees />
                        </div>
                    </FormGroup>
                </Form>
            </div>
        );
    }
}