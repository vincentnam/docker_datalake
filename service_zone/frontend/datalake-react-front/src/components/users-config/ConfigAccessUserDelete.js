import React from "react";
import api from '../../api/api';
import {Form, Button} from "react-bootstrap";
import {ToastContainer, toast} from 'react-toastify';
import {connect} from "react-redux";

class ConfigAccesUserDelete extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            user: {},
            selectRole: {},
            selectProject: {}
        };
        this.submitConfig = this.submitConfig.bind(this);
        this.close = this.close.bind(this);

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
        this.setState({
            user: this.props.selectElement,
            selectRole: this.props.selectElementAccess.role,
            selectProject: this.props.selectElementAccess.project
        });
    }

    submitConfig(event) {
        event.preventDefault();

        api.post('role_assignments/delete', {
            token: localStorage.getItem('token'),
            user: this.state.user.id,
            role: this.state.selectRole.id,
            project: this.state.selectProject.id
        })
            .then(() => {
                toast.success(`L'accès pour l'utilisateur ${this.state.user.name} sur le projet  ${this.state.selectProject.name} pour le rôle ${this.state.selectRole.name} a bien été supprimé !`, {
                    theme: "colored",
                    position: "top-right",
                    autoClose: 5000,
                    hideProgressBar: false,
                    closeOnClick: true,
                    pauseOnHover: true,
                    draggable: true,
                    progress: undefined,
                });
                this.close();
            })
            .catch(function (error) {
                console.log(error);
            });
    }

    close() {
        this.props.close(this.state.user, this.props.selectElementAccess);
        this.props.closeSecond(this.state.user);
    }

    render() {
        return (
            <div>
                <Form onSubmit={this.submitConfig}>
                    <div className="d-flex justify-content-between mt-4">
                        <Button className="btn buttonModel" type="submit">Valider</Button>
                        <Button
                            type="button"
                            className="btn buttonClose"
                            onClick={this.close}>
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

export default connect(mapStateToProps, null)(ConfigAccesUserDelete)