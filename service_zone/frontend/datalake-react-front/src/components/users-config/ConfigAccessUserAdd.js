import React from "react";
import {FormGroup, FormLabel, Form, Button} from "react-bootstrap";
import {ToastContainer, toast} from 'react-toastify';
import {connect} from "react-redux";
import Select from "react-select";
import {addUser, projects, roles, userRolesProjects} from "../../hook/Users-assignment-roles-projects/Users";

class ConfigAccesUserAdd extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            user: {},
            roles: [],
            projects: [],
            selectRole: "",
            selectProject: "",
            assignments: []
        };
        this.handleChangeRole = this.handleChangeRole.bind(this);
        this.handleChangeProject = this.handleChangeProject.bind(this);
        this.submitConfig = this.submitConfig.bind(this);
        this.loadRoles = this.loadRoles.bind(this);
        this.loadProjects = this.loadProjects.bind(this);
        this.loadUserRolesProjects = this.loadUserRolesProjects.bind(this);
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
        this.loadUserRolesProjects(this.props.selectElement);
        this.setState({
            user: this.props.selectElement,
        });
    }

    loadUserRolesProjects(user) {
        userRolesProjects(user, localStorage.getItem('token')).then((r) => {
            this.setState({assignments: r.userAccess})
        });
    }

    loadRoles() {
        roles(localStorage.getItem('token')).then((r) => {
            this.setState({roles: r.roles})
        });
    }

    loadProjects() {
        projects(localStorage.getItem('token')).then((r) => {
            this.setState({projects: r.projects})
        });
    }

    submitConfig(event) {
        event.preventDefault();
        let nbErrors = 0;
        if (this.state.user === {}) {
            this.toastError("Veuillez choisir un utilisateur !");
            nbErrors += 1;
        }
        if (this.state.selectRole.value === '') {
            this.toastError("Veuillez choisir un rôle !");
            nbErrors += 1;
        }
        if (this.state.selectProject.value === '') {
            this.toastError("Veuillez choisir un projet !");
            nbErrors += 1;
        }

        this.state.assignments.forEach((element) => {
            if (element.role.id === this.state.selectRole.value && element.project.id === this.state.selectProject.value) {
                this.toastError("Ce rôle et ce projet sont déjà assignés à cet utilisateur !");
                nbErrors += 1;
            }
        })

        if (nbErrors === 0) {
            addUser(this.state.user, this.state.selectRole, this.state.selectProject, localStorage.getItem('token')).then((r) => {
                if (r.result) {
                    toast.success(`Le nouvel accès pour l'utilisateur ${this.state.user.name} sur le projet  ${this.state.selectProject.label} et pour le rôle ${this.state.selectRole.label} a bien été configuré !`, {
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
            });
        }
    }

    handleChangeRole(event) {
        const name = "selectRole";
        this.setState({
            [name]: event,
        });
    }

    handleChangeProject(event) {
        const name = "selectProject";
        this.setState({
            [name]: event,
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
                                onChange={this.handleChangeRole}
                                name="role"
                                classNamePrefix="select"
                                options={this.state.roles}/>
                        </FormGroup>
                        <FormGroup style={{width: "45%"}}>
                            <FormLabel className="mt-2">Choisir un projet</FormLabel>
                            <Select
                                onChange={this.handleChangeProject}
                                name="project"
                                classNamePrefix="select"
                                options={this.state.projects}/>
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
                <ToastContainer/>
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

export default connect(mapStateToProps, null)(ConfigAccesUserAdd)