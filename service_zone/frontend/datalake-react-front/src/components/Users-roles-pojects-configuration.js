import React from "react";
import api from '../api/api';
import {connect} from "react-redux";
import {Button, Modal} from "react-bootstrap";
import {ToastContainer} from "react-toastify";
import ConfigAccessUserAdd from "./users-config/ConfigAccessUserAdd";
import ConfigAccessUserDelete from "./users-config/ConfigAccessUserDelete";
import ConfigAccessUserPurge from "./users-config/ConfigAccessUserPurge";

class UsersRolesProjectsConfiguration extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            modalShow: false,
            modalAdd: false,
            modalDelete: false,
            modalPurge: false,
            users: [],
            selectElement: {
                id: "",
                name: ""
            },
            selectElementAccess: {
                role: {name:""},
                project: {name:""}
            },
            userAccess: []
        };

        this.loadUsers = this.loadUsers.bind(this);
        this.loadUserRolesProjects = this.loadUserRolesProjects.bind(this);
        this.onChangeModalShow = this.onChangeModalShow.bind(this);
        this.onChangeModalShowSecond = this.onChangeModalShowSecond.bind(this);
        this.onChangeModalAdd = this.onChangeModalAdd.bind(this);
        this.onChangeModalDelete = this.onChangeModalDelete.bind(this);
        this.onChangeModalPurge = this.onChangeModalPurge.bind(this);
    }

    componentDidMount() {
        this.loadUsers();
    }

    loadUsers() {
        api.post('users', {
            token: localStorage.getItem('token')
        })
            .then((response) => {
                this.setState({
                    users: response.data.users
                });
            })
            .catch(function (error) {
                console.log(error);
            });
    }

    loadUserRolesProjects(user) {
        api.post('user_assignment', {
            token: localStorage.getItem('token'),
            user_id: user.id
        })
            .then((response) => {
                this.setState({
                    userAccess: response.data.assignment,
                    selectElement: user,
                    modalShow: !this.state.modalShow,
                });
            })
            .catch(function (error) {
                console.log(error);
            });
    }

    onChangeModalShow(element) {
        this.loadUserRolesProjects(element);
    }
    onChangeModalShowSecond(element) {
        this.setState({
            selectElement: element,
            modalShow: !this.state.modalShow,
        });
    }

    onChangeModalAdd(element) {
        this.setState({
            selectElement: element,
            modalAdd: !this.state.modalAdd,
        });
    }

    onChangeModalDelete(userAccess, elementAccess) {
        this.setState({
            userAccess: [
                {
                    "name": "",
                    "role": "",
                    "project": ""
                }
            ],
            selectElementAccess: elementAccess,
            modalDelete: !this.state.modalDelete,
        });
    }

    onChangeModalPurge() {
        this.setState({
            modalPurge: !this.state.modalPurge,
        });
    }

    render() {
        const TableUsers = () => {
            let dataUsers = "";
            if (this.state.users.length === 0) {
                dataUsers = (
                    <tr>
                        <td colSpan="5" align="center"><p>Il n'y a aucun utilisateurs !</p></td>
                    </tr>
                );
            } else {
                dataUsers = this.state.users.map((element, index) => (
                    <tr key={index}>
                        <td>{element.name}</td>
                        <td width="600px"></td>
                        <td>
                            <button type="button" className="btn btn-primary buttonModel"
                                    onClick={() => this.onChangeModalShow(element)}>Afficher les accès
                            </button>
                        </td>
                        <td>
                            <button type="button" className="btn btn-primary buttonModel"
                                    onClick={() => this.onChangeModalAdd(element)}>Ajouter un accès
                            </button>
                        </td>
                    </tr>
                ));
            }
            return (
                <table className="table table-traceability table-striped table-responsive" id="TableUsers">
                    <thead>
                    <tr style={{color: '#ea973b'}}>
                        <th>Login utilisateur</th>
                        <th></th>
                        <th>Afficher les accès</th>
                        <th>Ajouter un accès</th>
                    </tr>
                    </thead>
                    <tbody>
                    {dataUsers}
                    </tbody>
                </table>
            )
        }

        const TableAccesUser = (user) => {
            let dataAcces = "";
            if (this.state.userAccess.length === 0) {
                dataAcces = (
                    <tr>
                        <td colSpan="5" align="center"><p>L'utilisateur n'a aucun accès, veuillez lui en rajouter !</p></td>
                    </tr>
                );
            } else {
                dataAcces = this.state.userAccess.map((elementAccess, index) => (
                    <tr key={index}>
                        <td>{elementAccess.role.name}</td>
                        <td>{elementAccess.project.name}</td>
                        <td width="300px"></td>
                        <td>
                            <button type="button" className="btn btn-primary buttonModel"
                                    onClick={() => {
                                        this.onChangeModalDelete(this.state.userAccess, elementAccess);
                                        this.onChangeModalShowSecond(this.state.selectElement);
                                    }}>Supprimer l'accès
                            </button>
                        </td>
                    </tr>
                ));
            }
            return (
                <>
                    <table className="table table-traceability table-striped table-responsive" id="TableUsers">
                        <thead>
                        <tr style={{color: '#ea973b'}}>
                            <th>Rôle</th>
                            <th>Projet</th>
                            <th></th>
                            <th>Supprimer l'accès</th>
                        </tr>
                        </thead>
                        <tbody>
                        {dataAcces}
                        </tbody>
                    </table>
                    <div className="d-flex justify-content-between mt-4">
                        <Button
                            type="button"
                            className="btn buttonClose"
                            onClick={() => this.onChangeModalShow(this.state.selectElement)}>
                            Fermer
                        </Button>
                    </div>
                </>
            )
        }

        const ModalShow = () => {
            return (
                <Modal
                    size="lg"
                    show={this.state.modalShow}
                    onHide={() => this.onChangeModalShow({id: "", name: ""})}
                    aria-labelledby="model-show"
                >
                    <Modal.Header>
                        <Modal.Title id="model-show">
                            Les accès de l'utilisateur : "{this.state.selectElement.name}"
                        </Modal.Title>
                    </Modal.Header>
                    <Modal.Body>
                        <TableAccesUser/>
                    </Modal.Body>
                </Modal>
            )
        }

        const ModalDelete = () => {
            return (
                <Modal
                    size="lg"
                    show={this.state.modalDelete}
                    onHide={() => this.onChangeModalDelete({name: "",})}
                    aria-labelledby="model-delete"
                >
                    <Modal.Header>
                        <Modal.Title id="model-delete">
                            Supprimer l'accès : Utilisateur : "{this.state.selectElement.name}", Rôle : "{this.state.selectElementAccess.role.name}", Projet : "{this.state.selectElementAccess.project.name}"
                        </Modal.Title>
                    </Modal.Header>
                    <Modal.Body>
                        <ConfigAccessUserDelete
                            selectElement={this.state.selectElement}
                            selectElementAccess={this.state.selectElementAccess}
                            close={this.onChangeModalDelete}
                            closeSecond={this.onChangeModalShow}
                            reload={this.loadUserRolesProjects}
                        />
                    </Modal.Body>
                </Modal>
            )
        }

        const ModalAdd = () => {
            return (
                <Modal
                    size="lg"
                    show={this.state.modalAdd}
                    onHide={() => this.onChangeModalAdd({id: "", name: ""})}
                    aria-labelledby="model-add"
                >
                    <Modal.Header>
                        <Modal.Title id="model-add">
                            Ajouter un accès à l'utilisateur : "{this.state.selectElement.name}"
                        </Modal.Title>
                    </Modal.Header>
                    <Modal.Body>
                        <ConfigAccessUserAdd
                            selectElement={this.state.selectElement}
                            close={this.onChangeModalAdd}
                            reload={this.loadUsers}
                        />
                    </Modal.Body>
                </Modal>
            )
        }

        const ModalPurge = () => {
            return (
                <Modal
                    size="lg"
                    show={this.state.modalPurge}
                    aria-labelledby="model-purge"
                >
                    <Modal.Header>
                        <Modal.Title id="model-purge">
                            Purge des utilisateurs supprimés dans LDAP
                        </Modal.Title>
                    </Modal.Header>
                    <Modal.Body>
                        <ConfigAccessUserPurge
                            close={this.onChangeModalPurge}
                        />
                    </Modal.Body>
                </Modal>
            )
        }
        
        return (
            <div className="container main-upload">
                <div className="title">
                <table>
                <tr>
                    <td  width="500px" align="left">Configuration des accès utilisateurs :</td>
                    <td  width="500px" align="right">
                        <button type="button" className="btn btn-primary buttonModel"
                            onClick={() => this.onChangeModalPurge()}>Purge des utilisateurs
                        </button>
                    </td>
                </tr>
                </table> 
                </div>
                <div className="data-table">
                    <TableUsers/>
                    <ModalShow/>
                    <ModalAdd/>
                    <ModalDelete/>
                    <ModalPurge/>
                </div>
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

export default connect(mapStateToProps, null)(UsersRolesProjectsConfiguration)