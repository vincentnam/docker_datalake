import React from "react";
import ModelAddForm from './model/ModelAddForm';
import ModelEditForm from './model/ModelEditForm';
import { Button } from "react-bootstrap";
import api from '../api/api';
import { ToastContainer } from 'react-toastify';
import {connect} from "react-redux";

class Models extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            models: [],
            modelsCache: [],
            model: {},
            newModel: {},
            show: "",
            container_name: "",
        };
        this.loadModel = this.loadModel.bind(this);
        this.formAdd = this.formAdd.bind(this);
        this.handleCallShow = this.handleCallShow.bind(this);
        this.editChange = this.editChange.bind(this);
        this.loadRolesProjectsUser = this.loadRolesProjectsUser.bind(this);
    }

    componentDidMount() {
        if (this.props.nameContainer.nameContainer !== "") {
            this.setState({
                container_name: this.props.nameContainer.nameContainer,
            })
            this.loadModel();
        } else {
            this.loadRolesProjectsUser();
        }

    }

    loadRolesProjectsUser() {
        api.post('auth-token/projects', {
            token: localStorage.getItem('token')
        })
            .then((response) => {
                let listProjectAccess = [];
                response.data.projects.forEach((project) => {
                    if (project.name !== "datalake" && project.name !== "admin") {
                        listProjectAccess.push({
                            label: project.name,
                            name_container: project.name,
                        })
                    }
                });
                this.setState({
                    container_name: listProjectAccess[0].name_container,
                })
                this.loadModel();
            })
            .catch(function (error) {
                console.log(error);
            });
    }

    loadModel() {
        api.post('models/show/all', {
            container_name: this.props.nameContainer.nameContainer,
            token: localStorage.getItem('token')
        })
            .then((response) => {
                this.setState({
                    models: response.data.models.data,
                });
            })
            .catch(function (error) {
                console.log(error);
            });

        api.post('models/cache/all', {
            container_name: this.props.nameContainer.nameContainer,
            token: localStorage.getItem('token')
        })
            .then((response) => {
                console.log()
                this.setState({
                    modelsCache: response.data.models.data
                });
            })
            .catch(function (error) {
                console.log(error);
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

    formAdd() {
        this.setState({
            model: {},
            show: "add",
        });
    }

    handleCallLoadModels = () => {
        this.loadModel();
    }

    handleCallShow = () => {
        this.setState({
            show: "",
        });
    }

    editChange = (model) => {
        this.setState({
            show: "edit",
            model: model
        });
    }

    render() {

        const Formulaire = () => {
            if (this.state.show === "") {
                return (
                    <div></div>
                );
            } else if (this.state.show === "add") {
                return (
                    <ModelAddForm
                        loading={this.handleCallLoadModels}
                        show={this.handleCallShow}
                    />
                );
            } else if (this.state.show === "edit") {
                return (
                    <ModelEditForm
                        loading={this.handleCallLoadModels}
                        show={this.handleCallShow}
                        modelEdit={this.state.model}
                    />
                );
            }
        };

        const ListModels = () => {
            const AllModels = this.state.models.map((model) => (
                <span><button className="mt-2 modelsList" key={model._id} onClick={() => this.editChange(model)}><b>{model.label}</b></button><br/></span>
            ));
            const AllModelsCache = this.state.modelsCache.map((model) => (
                <span><button className="mt-2 modelsList-cacher" key={model._id} onClick={() => this.editChange(model)}><b>{model.label}</b></button><br/></span>
            ));

            return (
                <div className="col-sm-2 pt-2 pb-2 meta">
                    <h6><b>Liste des modèles de métadonnées visibles</b></h6>
                    <div className="list-button">
                        {AllModels}
                    </div>

                    <h6 className="mt-4"><b>Liste des modèles de métadonnées cachés</b></h6>
                    <div className="list-button">
                        {AllModelsCache}
                    </div>
                </div>
            );
        };

        return (
            <div>
                <div className="container mt-4 mb-4">
                    <h3>Gestion des modèles dynamiques de métadonnées
                        <Button className="btn buttonModel btn-sm m-2" onClick={this.formAdd}>Ajouter</Button>
                    </h3>
                    <div className="row d-flex justify-content-between mt-4">
                        <ListModels />
                        <Formulaire />
                    </div>
                    <ToastContainer />
                </div>
            </div>
        );
    }
}
const mapStateToProps = (state) => {
    return {
        nameContainer: state.nameContainer,
        auth: state.auth
    }
}

export default connect(mapStateToProps, null)(Models)