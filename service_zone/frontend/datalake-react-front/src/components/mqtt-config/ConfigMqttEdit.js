import React from "react";
import { FormGroup, FormLabel, Form, Button } from "react-bootstrap";
import { ToastContainer, toast } from 'react-toastify';
import {connect} from "react-redux";
import {mqttEdit} from "../../hook/Mqtt/Mqtt";

class ConfigMqttEdit extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            name: "",
            oldName: "",
            description: "",
            url: "",
            user: "",
            password: "",
            batchDuration: 0,
            topic: "",
            passwordShown: false,
            status: true,
        };
        this.handleChange = this.handleChange.bind(this);
        this.handleChangeStatus = this.handleChangeStatus.bind(this);
        this.submitConfig = this.submitConfig.bind(this);
        this.togglePassword = this.togglePassword.bind(this);
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
            name: this.props.selectElement.name,
            oldName: this.props.selectElement.name,
            description: this.props.selectElement.description,
            url: this.props.selectElement.brokerUrl,
            user: this.props.selectElement.user,
            password: this.props.selectElement.password,
            batchDuration: this.props.selectElement.batchDuration,
            topic: this.props.selectElement.topic,
            status: this.props.selectElement.status,
        });
    }

    submitConfig(event) {
        event.preventDefault();

        let nbErrors = 0;

        if (this.state.oldName !== this.state.name){
            this.props.listElements.forEach((config) => {
                if (this.state.name.trim() === config.name.trim()) {
                    this.toastError("Veuillez renseigner un nom de flux mqtt n'est pas déjà utilisé !");
                    nbErrors += 1;
                }
            });
        }

        if (this.state.name.trim() === '') {
            this.toastError("Veuillez renseigner un nom de flux !");
            nbErrors += 1;
        }
        if (this.state.url.trim() === '') {
            this.toastError("Veuillez renseigner un url valide !");
            nbErrors += 1;
        }
        if (this.state.user.trim() === '') {
            this.toastError("Veuillez renseigner un user valide !");
            nbErrors += 1;
        }
        if (this.state.password.trim() === '') {
            this.toastError("Veuillez renseigner un mot de passe valide !");
            nbErrors += 1;
        }
        if (this.state.topic.trim() === '') {
            this.toastError("Veuillez renseigner un topic valide !");
            nbErrors += 1;
        }

        if (nbErrors === 0) {
            const mqtt = mqttEdit(this.props.selectElement._id, this.state.name, this.state.description, this.state.url, this.state.user, this.state.password, this.state.topic, this.state.status, this.props.containerName, localStorage.getItem('token'))
            mqtt.then((response) => {
                if (response.result === true) {
                    this.props.reload();
                    this.props.close(this.props.selectElement);
                    toast.success(`Le flux ${this.state.name} à bien été modifié !`, {
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

    handleChange(event) {
        const target = event.target;
        const value = target.type === 'checkbox' ? target.checked : target.value;
        const name = target.name;

        this.setState({
            [name]: value,
        });
    }

    handleChangeStatus() {
        this.setState({
            status: !this.state.status,
        });
    };

    togglePassword() {
        this.setState({
            passwordShown: !this.state.passwordShown,
        });
    };

    render() {
        return (
            <div>
                <Form onSubmit={this.submitConfig}>
                    <FormGroup>
                        <FormLabel>Nom du flux</FormLabel>
                        <Form.Control
                            type="text"
                            placeholder="Nom du flux"
                            name="name"
                            value={this.state.name}
                            onChange={this.handleChange}
                        />
                    </FormGroup>
                    <FormGroup>
                        <FormLabel>Description</FormLabel>
                        <Form.Control
                            as="textarea"
                            rows={3}
                            placeholder="Description"
                            name="description"
                            value={this.state.description}
                            onChange={this.handleChange}
                        />
                    </FormGroup>
                    <FormGroup>
                        <FormLabel>Url de destination</FormLabel>
                        <Form.Control
                            type="text"
                            placeholder="Url de destination"
                            name="url"
                            value={this.state.url}
                            onChange={this.handleChange}
                        />
                    </FormGroup>
                    <FormGroup>
                        <FormLabel>User</FormLabel>
                        <Form.Control
                            type="text"
                            placeholder="User"
                            name="user"
                            value={this.state.user}
                            onChange={this.handleChange}
                        />
                    </FormGroup>
                    <FormGroup>
                        <FormLabel>Password</FormLabel>
                        <Form.Control
                            type={this.state.passwordShown ? "text" : "password"}
                            placeholder="Password"
                            name="password"
                            value={this.state.password}
                            onChange={this.handleChange}
                        />
                        <Button className="btn btn-primary buttonModel" onClick={this.togglePassword}>Show Password</Button>
                    </FormGroup>
                    <FormGroup>
                        <FormLabel>Status</FormLabel>
                        <Form.Check
                            type="checkbox"
                            label="(Cocher pour activer, Décocher pour désactiver)"
                            checked={this.state.status}
                            onChange={this.handleChangeStatus}/>
                    </FormGroup>
                    <FormGroup>
                        <FormLabel>Topic</FormLabel>
                        <Form.Control
                            type="text"
                            placeholder="Topic"
                            name="topic"
                            value={this.state.topic}
                            onChange={this.handleChange}
                        />
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
const mapStateToProps = (state) => {
    return {
        nameContainer: state.nameContainer,
        auth: state.auth
    }
}

export default connect(mapStateToProps, null)(ConfigMqttEdit)