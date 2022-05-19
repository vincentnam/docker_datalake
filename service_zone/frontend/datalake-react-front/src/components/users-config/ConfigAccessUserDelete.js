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
            selectRole: "",
            selectProject: ""
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

        api.post('deleteAccess', {
            token: localStorage.getItem('token'),
            user: this.state.user,
            role: this.state.selectRole,
            project: this.state.user
        })
            .then(() => {
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

    close() {
        let val = [
            {
                "name": "tlegagneur",
                "role": "PowerUsers",
                "project": "NeOCampus"
            }
        ]
        this.props.close(this.state.user, val);
        this.props.closeSecond(val);
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