import React from "react";
import {Form, Button} from "react-bootstrap";
import {ToastContainer, toast} from 'react-toastify';
import {connect} from "react-redux";
import {mqttEditStatus} from "../../hook/Mqtt/Mqtt";

class ConfigMqttChangeStatus extends React.Component {
    constructor(props) {
        super(props);
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

    submitConfig(event) {
        event.preventDefault();
        const mqttStatus = mqttEditStatus(this.props.selectElement._id, !this.props.selectElement.status, localStorage.getItem('token'))
        mqttStatus.then((response) => {
            if (response.result === true) {
                this.props.reload();
                this.props.close(this.props.selectElement);
                toast.success(`Le status du flux ${this.props.selectElement.name} à bien été changé !`, {
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

    render() {
        return (
            <div>
                <Form onSubmit={this.submitConfig}>
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

export default connect(mapStateToProps, null)(ConfigMqttChangeStatus)