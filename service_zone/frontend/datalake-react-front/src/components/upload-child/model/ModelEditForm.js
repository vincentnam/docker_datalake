import React from "react";
import api from '../../../api/api';
import { FormGroup, FormLabel, Form, Button } from "react-bootstrap";
import Select from 'react-select';
import { types_files } from '../../../configmeta/types_files';
import { MetadonneesEditForm } from './MetadonneesEditForm';
import { ToastContainer, toast } from 'react-toastify';

export class ModelEditForm extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            label: "",
            metadonnees: [],
            meta: {
                id: 0,
                label: "",
                type: "",
                name: ""
            },
            status: "",
            typesFiles: types_files,
            selectedTypesFiles: null,
            verifModels: [],
            oldLabel: ""
        };
        this.handleChange = this.handleChange.bind(this);
        this.handleChangeType = this.handleChangeType.bind(this);
        this.submitModels = this.submitModels.bind(this);
        this.addMeta = this.addMeta.bind(this);
        this.deleteMeta = this.deleteMeta.bind(this);
        this.handleChangeMeta = this.handleChangeMeta.bind(this);
    }

    componentDidMount() {
        let selectedTypes = []
        this.props.editModel.typesFiles.forEach((type) => {
            selectedTypes.push({
                value: type,
                label: type
            })
        });

        this.setState({
            selectedTypesFiles: selectedTypes,
            metadonnees: this.props.editModel.metadonnees,
            label: this.props.editModel.label,
            oldLabel: this.props.editModel.label,
            status: this.props.editModel.status,
        });

        api.get('models/all')
            .then((response) => {
                this.setState({
                    verifModels: response.data.models.data
                });
            })
            .catch(function (error) {
                console.log(error);
            });
    }

    toastError(message) {
        toast.error(`${message}`, {
            theme: "colored",
            position: "top-right",
            autoClose: 5000,
            hideProgressBar: false,
            closeOnClick: true,
            pauseOnHover: true,
            draggable: true,
            progress: undefined,
        });
    }

    submitModels(event) {
        event.preventDefault();
        let types = [];
        this.state.selectedTypesFiles.forEach(type => types.push(type.value));

        let nbErrors = 0;

        if(this.state.label.trim() !== this.state.oldLabel.trim()) {
            this.state.verifModels.forEach((model) => {
                if (this.state.label === model.label) {
                    this.toastError("Veuillez renseigner un label de modèle de métadonnées qui n'est pas déjà utilisé !");
                    nbErrors += 1;
                }
            });
        }

        if (this.state.label.trim() === '') {
            this.toastError("Veuillez renseigner un label de modèle de métadonnées !");
            nbErrors += 1;
        }

        if (types.length === 0) {
            this.toastError("Veuillez ajouter au minimum un type de fichier accepté !");
            nbErrors += 1;
        }

        if (this.state.metadonnees.length === 0) {
            this.toastError("Veuillez ajouter au minimum une métadonnée !");
            nbErrors += 1;
        }

        if (this.state.metadonnees.length !== 0) {
            this.state.metadonnees.forEach((meta) => {
                if (meta.label.trim() === "" || meta.type.trim() === "" || meta.name.trim() === "") {
                    this.toastError("Veuillez renseigner les informations dans les champs des métadonnées !");
                    nbErrors += 1;
                }
            });
        }

        if (nbErrors === 0) {
            api.post('models/edit', {
                id: this.props.editModel.id,
                label: this.state.label,
                type_file_accepted: types,
                metadonnees: this.state.metadonnees,
                status: this.state.status
            })
                .then(() => {
                    this.props.reload();
                    this.props.close();
                    toast.success(`Le modèle ${this.state.label} à bien été modifié !`, {
                        theme: "colored",
                        position: "top-right",
                        autoClose: 5000,
                        hideProgressBar: false,
                        closeOnClick: true,
                        pauseOnHover: true,
                        draggable: true,
                        progress: undefined,
                    });
                })
                .catch(function (error) {
                    console.log(error);
                });
        }
    }

    handleChangeType(event) {
        const name = "selectedTypesFiles";
        this.setState({
            [name]: event,
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
        let lastNumber = 0;
        if (totalMetadonnees > 0) {
            lastNumber = this.state.metadonnees[totalMetadonnees - 1].id;
        }
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
            if (d.id !== id) {
                afterdelete.push(d);
            }
        });

        this.setState({
            [name]: afterdelete
        });
    }

    handleChangeMeta(event, id) {
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
                <MetadonneesEditForm
                    value={id = id + 1}
                    meta={meta}
                    metadonnees={this.state.metadonnees}
                    onDeleteMeta={this.deleteMeta}
                    onHandleChange={this.handleChangeMeta}
                    key={id}
                />
            ));

            return (
                <div className="row d-flex justify-content-around col-sm-12">
                    {listMetadonnees}
                </div>
            );
        }

        return (
            <div className="">
                <div className="d-flex justify-content-between">
                    <h5>Modification d'un modèle de métadonnées</h5>
                    <Form.Group className="mb-3 checkboxModel" controlId="status">
                        <Form.Check 
                            type="checkbox"
                            checked={this.state.status}
                            name="status"
                            id="status"
                            onChange={this.handleChange}
                            label="Rendre visible le model"
                            className="checkboxModel"
                        />
                    </Form.Group>
                </div>
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
                            value={this.state.selectedTypesFiles}
                            options={this.state.typesFiles} />
                    </FormGroup>
                    <FormGroup className="mt-2">
                        <div>
                            <FormLabel>Métadonnées</FormLabel>
                            <Button className="btn buttonModel btn-primary btn-sm m-2" onClick={this.addMeta}>Ajouter</Button>
                        </div>
                        <Metadonnees />
                    </FormGroup>
                    <div className="d-flex justify-content-between mt-4">
                        <Button className="btn buttonModel" type="submit">Valider</Button>
                        <Button
                            type="button"
                            className="btn buttonClose"
                            onClick={this.props.close}>
                            Fermer
                        </Button>
                    </div>
                </Form>
                <ToastContainer />
            </div >
        );
    }
}