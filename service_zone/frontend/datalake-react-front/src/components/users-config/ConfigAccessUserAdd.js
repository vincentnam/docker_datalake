import React from "react";
import api from '../../api/api';
import { FormGroup, FormLabel, Form, Button } from "react-bootstrap";
import { ToastContainer, toast } from 'react-toastify';
import {connect} from "react-redux";
import Select from "react-select";

class ConfigAccesUserAdd extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            user: {},
            roles: [],
            projects: [],
            selectRole: "",
            selectProject: ""
        };
        this.handleChange = this.handleChange.bind(this);
        this.submitConfig = this.submitConfig.bind(this);
        this.loadRoles = this.loadRoles.bind(this);
        this.loadProjects = this.loadProjects.bind(this);
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

    componentDidMount() {
        this.loadRoles();
        this.loadProjects();
        this.setState({
            user: this.props.selectElement,
        });
        console.log(this.props.selectElement);
    }

    loadRoles(){
        console.log("load roles")
        api.post('roles', {
            token: localStorage.getItem('token')
        })
            .then((response) => {
                this.setState({
                    roles: response.data.roles
                });
            })
            .catch(function (error) {
                console.log(error);
            });
    }

    loadProjects(){
        console.log("load projects")
        api.post('projects', {
            token: localStorage.getItem('token')
        })
            .then((response) => {
                this.setState({
                    projects: response.data.projects
                });
            })
            .catch(function (error) {
                console.log(error);
            });
    }

    submitConfig(event) {
        event.preventDefault();
        let nbErrors = 0;

        if (this.state.user === {}) {
            this.toastError("Veuillez choisir un utilisateur !");
            nbErrors += 1;
        }
        if (this.state.selectRole.trim() === '') {
            this.toastError("Veuillez choisir un rôle !");
            nbErrors += 1;
        }
        if (this.state.selectProject.trim() === '') {
            this.toastError("Veuillez choisir un projet !");
            nbErrors += 1;
        }

        if (nbErrors === 0) {
            api.post('user/add', {
                token: localStorage.getItem('token'),
                user: this.props.user,
                role: this.state.selectRole,
                project: this.state.selectProject,
            })
                .then(() => {
                    this.props.reload();
                    this.props.close(this.props.selectElement);
                    toast.success(`Le nouvel accès pour l'utilisateur ${this.state.user.name} a bien été configuré !`, {
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

    handleChange(event) {
        const target = event.target;
        const value = target.type === 'checkbox' ? target.checked : target.value;
        const name = target.name;

        this.setState({
            [name]: value,
        });
    }

    render() {
        return (
            <div>
                <Form onSubmit={this.submitConfig}>
                    <div className="d-flex justify-content-around">
                        <FormGroup style={{width: "45%"}}>
                            <FormLabel className="mt-2">Choisir un rôle</FormLabel>
                            <Select
                                onChange={this.handleChange}
                                name="role"
                                classNamePrefix="select"
                                options={this.state.roles} />
                        </FormGroup>
                        <FormGroup style={{width: "45%"}}>
                            <FormLabel className="mt-2">Choisir un projet</FormLabel>
                            <Select
                                onChange={this.handleChange}
                                name="project"
                                classNamePrefix="select"
                                options={this.state.projects} />
                        </FormGroup>
                    </div>
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
const mapStateToProps = (state) => {
    return {
        nameContainer: state.nameContainer,
        auth: state.auth
    }
}

export default connect(mapStateToProps, null)(ConfigAccesUserAdd)