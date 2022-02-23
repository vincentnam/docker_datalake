import React from "react";
import api from '../../api/api';
import { FormGroup, FormLabel, Form, Button } from "react-bootstrap";
import { ToastContainer, toast } from 'react-toastify';
import {connect} from "react-redux";

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
        };
        this.handleChange = this.handleChange.bind(this);
        this.submitConfig = this.submitConfig.bind(this);
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
        if (this.state.batchDuration <= 0) {
            this.toastError("Veuillez renseigner un batch duration supérieur à 0 !");
            nbErrors += 1;
        }
        if (this.state.topic.trim() === '') {
            this.toastError("Veuillez renseigner un topic valide !");
            nbErrors += 1;
        }

        if (nbErrors === 0) {
            api.post('mqtt/edit', {
                id: this.props.selectElement._id,
                name: this.state.name,
                description: this.state.description,
                brokerUrl: this.state.url,
                user: this.state.user,
                password: this.state.password,
                batchDuration: this.state.batchDuration,
                topic: this.state.topic,
                container_name: this.props.containerName,
                status: this.props.selectElement.status,
            })
                .then(() => {
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
                            type="password"
                            placeholder="Password"
                            name="password"
                            value={this.state.password}
                            onChange={this.handleChange}
                        />
                    </FormGroup>
                    <FormGroup>
                        <FormLabel>Batch duration</FormLabel>
                        <Form.Control
                            type="number"
                            placeholder="batchDuration"
                            name="batchDuration"
                            value={this.state.batchDuration}
                            onChange={this.handleChange}
                            min={0}
                        />
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
    }
}

export default connect(mapStateToProps, null)(ConfigMqttEdit)