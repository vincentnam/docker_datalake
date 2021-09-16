import React from "react";
import api from '../../api/api';
import { FormGroup, FormLabel, Form, Button } from "react-bootstrap";
import Select from 'react-select';
import { types_files } from '../../configmeta/types_files';
import { MetadonneesForm } from './MetadonneesForm';

export class ModelAddForm extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            metadonnees: [
                {
                    id: 1,
                    label: "test1",
                    type: "text",
                    name: "text12"
                }
            ],
            meta: {
                id: 0,
                label: "",
                type: "",
                name: ""
            },
            label: "",
            newModel: {},
            typesFiles: types_files,
            selectedTypesFiles: null
        };
        this.handleChange = this.handleChange.bind(this);
        this.handleChangeType = this.handleChangeType.bind(this);
        this.submitModels = this.submitModels.bind(this);
        this.addMeta = this.addMeta.bind(this);
        this.deleteMeta = this.deleteMeta.bind(this);
        this.handleChangeMeta = this.handleChangeMeta.bind(this);
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

    submitModels(event) {
        event.preventDefault();
        console.log('add');
        console.log(this.state.label);
        console.log(this.state.selectedTypesFiles);
        console.log(this.state.metadonnees);
        api.post('models/add', {
            label: this.state.label,
            type_file_accepted: this.state.selectedTypesFiles,
            metadonnees: this.state.metadonnees
        })
            .then((response) => {
                console.log(response)
            })
            .catch(function (error) {
                console.log(error);
            });
    }

    handleChangeType(event) {
        let types = [];
        event.forEach(type => types.push(type.value));
        const name = "selectedTypesFiles";
        this.setState({
            [name]: types,
        });
    }

    handleChange(event) {
        const target = event.target;
        const value = target.type === 'checkbox' ? target.checked : target.value;
        const name = target.name;

        this.setState({
            [name]: value,
        });
    }

    addMeta() {
        const name = "metadonnees";
        let data = Array.from(this.state.metadonnees);
        let totalMetadonnees = data.length;
        let lastNumber = this.state.metadonnees[totalMetadonnees - 1].id;
        console.log(lastNumber);
        data.push(
            {
                id: lastNumber + 1,
                label: "",
                type: "",
                name: ""
            }
        );
        this.setState({
            [name]: data
        });
    }

    deleteMeta(id) {
        const name = "metadonnees";
        let data = Array.from(this.state.metadonnees);
        let afterdelete = [];
        data.forEach(d => {
            if(d.id != id) {
                afterdelete.push(d);
            }
        });

        this.setState({
            [name]: afterdelete
        });
    }

    handleChangeMeta(event, id) {

        console.log(event);
        console.log(id);
        const name = "metadonnees";
        const target = event.target;
        const value = target.type === 'checkbox' ? target.checked : target.value;
        const valueName = target.name;

        let data = this.state.metadonnees;

        if (valueName === "label") {
            data[id - 1].label = value;
        }
        if (valueName === "type") {
            data[id - 1].type = value;
        }
        if (valueName === "name") {
            data[id - 1].name = value;
        }
        this.setState({
            [name]: data
        });
    }

    //handleCallbackData = (childData) =>{
    //    this.setState({dataFilters: childData})
    //}

    render() {
        let Metadonnees = () => {
            let data = Array.from(this.state.metadonnees);
            let id = 0;
            let listMetadonnees = data.map((meta) => (
                <MetadonneesForm
                    value={id = id + 1}
                    meta={meta}
                    onDeleteMeta={this.deleteMeta}
                    onHandleChange={this.handleChangeMeta}
                />
            ));

            return (
                <div className="row d-flex justify-content-around col-sm-12">
                    {listMetadonnees}
                </div>
            );
        }

        return (
            <div className="col-sm-10 card pt-2 pb-2">
                <h5>Ajout d'un modèle de métadonnées</h5>
                <Form onSubmit={this.submitModels}>
                    <FormGroup>
                        <FormLabel>Label</FormLabel>
                        <Form.Control
                            type="text"
                            placeholder="Label du modèle"
                            name="label"
                            value={this.state.label}
                            onChange={this.handleChange}
                        />
                    </FormGroup>
                    <FormGroup>
                        <FormLabel className="mt-2">Types de fichiers</FormLabel>
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
                            <Button className="btn btn-primary btn-sm m-2" onClick={this.addMeta}>Ajouter</Button>
                        </div>
                        <Metadonnees />
                    </FormGroup>
                    <Button className="btn btn-primary" type="submit">Valider</Button>
                </Form>
            </div >
        );
    }
}