import React from "react";
import api from '../api/api';
import {Modal} from 'react-bootstrap';
import {connect} from "react-redux";
import ConfigMqttAdd from "./mqtt-config/ConfigMqttAdd";
import ConfigMqttEdit from "./mqtt-config/ConfigMqttEdit";
import ConfigMqttChangeStatus from "./mqtt-config/ConfigMqttChangeStatus";
import {ToastContainer} from 'react-toastify';

class MqttConfigList extends React.Component {
    constructor(props) {
        super(props);
        // Set some state
        this.state = {
            elements: [],
            offset: 0,
            perPage: 10,
            sort_value: 1,
            sort_field: '',
            modalAdd: false,
            modalEdit: false,
            modalStatus: false,
            selectElement: {
                name: "",
            },
            statusFluxAll: true,
        };
        this.loadMqttConfig = this.loadMqttConfig.bind(this);
        this.onChangeModalAdd = this.onChangeModalAdd.bind(this);
        this.onChangeModalEdit = this.onChangeModalEdit.bind(this);
        this.loadMqttConfigStatus = this.loadMqttConfigStatus.bind(this);
        this.onChangeModalElementStatus = this.onChangeModalElementStatus.bind(this);
        this.loadFlux = this.loadFlux.bind(this);
    }

    componentDidMount() {
        this.loadMqttConfig();
    }

    loadMqttConfig() {
        api.post('mqtt/all', {
            container_name: this.props.nameContainer.nameContainer,
            token: localStorage.getItem('token')
        })
            .then((response) => {
                this.setState({
                    elements: response.data.list_flux.data
                });
            })
            .catch(function (error) {
                console.log(error);
            });
    }

    loadMqttConfigStatus() {
        api.post('mqtt/status/actif', {
            container_name: this.props.nameContainer.nameContainer,
            token: localStorage.getItem('token')
        })
            .then((response) => {
                this.setState({
                    elements: response.data.list_flux.data,
                });
            })
            .catch(function (error) {
                console.log(error);
            });
    }

    loadFlux() {
        if (this.state.statusFluxAll === true){
            this.loadMqttConfig();
        } else {
            this.loadMqttConfigStatus();
        }
    }

    onChangeModalAdd() {
        this.setState({
            modalAdd: !this.state.modalAdd,
        });
    }

    onChangeModalEdit(element) {
        this.setState({
            selectElement: element,
            modalEdit: !this.state.modalEdit,
        });
    }

    onChangeModalElementStatus(element) {
        this.setState({
            selectElement: element,
            modalStatus: !this.state.modalStatus,
        });
    }

    onChangeStatusFlux() {
        if (this.state.statusFluxAll === true){
            this.setState({
                statusFluxAll: !this.state.statusFluxAll,
            });
            this.loadMqttConfigStatus();
        } else {
            this.setState({
                statusFluxAll: !this.state.statusFluxAll,
            });
            this.loadMqttConfig();
        }
    }

    render() {
        const TableMqttConfig = () => {
            let dataMqttConfig = "";
            if (this.state.elements.length === 0) {
                dataMqttConfig = (
                    <tr>
                        <td colSpan="5" align="center"><p>Il n'y a aucune configuration de flux MQTT !</p></td>
                    </tr>
                );
            } else {
                const StatusButton = (props) => {
                    const status = props.element.status;
                    if (status) {
                        return <button type="button" className="btn btn-success"
                                       onClick={() => this.onChangeModalElementStatus(props.element)}>En cours</button>;
                    }
                    return <button type="button" className="btn btn-danger"
                                   onClick={() => this.onChangeModalElementStatus(props.element)}>Arrêté</button>;
                }

                dataMqttConfig = this.state.elements.map((element, index) => (
                    <tr key={index}>
                        <td>{element.name}</td>
                        <td><span className="text-break">{element.description}</span></td>
                        <td>{element.brokerUrl}</td>
                        <td>{element.topic}</td>
                        <td>
                            <button type="button" className="btn btn-primary buttonModel"
                                    onClick={() => this.onChangeModalEdit(element)}>Modifier
                            </button>
                        </td>
                        <td>
                            <StatusButton element={element}/>
                        </td>
                    </tr>
                ));
            }
            return (
                <table className="table table-traceability table-striped table-responsive" id="TableMqttConfig">
                    <thead>
                    <tr style={{color: '#ea973b'}}>
                        <th>Nom du flux</th>
                        <th>Description</th>
                        <th>Url</th>
                        <th>Topic</th>
                        <th>Modifier</th>
                        <th>Status</th>
                    </tr>
                    </thead>
                    <tbody>
                    {dataMqttConfig}
                    </tbody>
                </table>
            )
        }

        const ModalAdd = () => {
            return (
                <Modal
                    size="lg"
                    show={this.state.modalAdd}
                    onHide={() => this.onChangeModalAdd()}
                    aria-labelledby="model-add"
                >
                    <Modal.Header>
                        <Modal.Title id="model-add">
                            Ajouter un flux MQTT
                        </Modal.Title>
                    </Modal.Header>
                    <Modal.Body>
                        <ConfigMqttAdd
                            containerName={this.props.nameContainer.nameContainer}
                            listElements={this.state.elements}
                            close={this.onChangeModalAdd}
                            reload={this.loadFlux}
                        />
                    </Modal.Body>
                </Modal>
            )
        }
        const ModalEdit = () => {
            return (
                <Modal
                    size="lg"
                    show={this.state.modalEdit}
                    onHide={() => this.onChangeModalEdit({name: "",})}
                    aria-labelledby="model-edit"
                >
                    <Modal.Header>
                        <Modal.Title id="model-edit">
                            Modifier un flux MQTT : "{this.state.selectElement.name}"
                        </Modal.Title>
                    </Modal.Header>
                    <Modal.Body>
                        <ConfigMqttEdit
                            containerName={this.props.nameContainer.nameContainer}
                            listElements={this.state.elements}
                            selectElement={this.state.selectElement}
                            close={this.onChangeModalEdit}
                            reload={this.loadFlux}
                        />
                    </Modal.Body>
                </Modal>
            )
        }

        const ModalChangeStatus = () => {
            let message = "";
            if(this.state.selectElement.status) {
                message = "Voulez-vous désactiver le flux MQTT : " +this.state.selectElement.name +" ?";
            } else {
                message = "Voulez-vous activer le flux MQTT : " +this.state.selectElement.name +" ?";
            }
            
            return (
                <Modal
                    size="lg"
                    show={this.state.modalStatus}
                    onHide={() => this.onChangeModalElementStatus({name: "",})}
                    aria-labelledby="model-change"
                >
                    <Modal.Header>
                        <Modal.Title id="model-change">
                            {message}
                        </Modal.Title>
                    </Modal.Header>
                    <Modal.Body>
                        <ConfigMqttChangeStatus
                            selectElement={this.state.selectElement}
                            close={this.onChangeModalElementStatus}
                            reload={this.loadFlux}
                        />
                    </Modal.Body>
                </Modal>
            )
        }

        const ButtonStatus = () => {
            if(this.state.statusFluxAll === true) {
                return (
                    <button type="button" className="btn btn-primary buttonModel"
                            onClick={() => this.onChangeStatusFlux()}>Afficher les flux actifs
                    </button>
                );
            } else {
                return (
                    <button type="button" className="btn btn-success"
                            onClick={() => this.onChangeStatusFlux()}>Afficher tous les flux
                    </button>
                );
            }
        }

        return (
            <div className="container main-download mt-4">
                <nav className="tab-show">
                    <div className="nav nav-pills" id="pills-tab" role="tablist">
                        <button className="nav-link active" id="nav-flux-mqtt" data-bs-toggle="pill"
                                data-bs-target="#nav-raw" type="button" role="tab" aria-controls="nav-raw"
                                aria-selected="true">Configuration des flux MQTT
                        </button>
                    </div>
                </nav>
                <div className="tab-content mt-2" id="pills-tabContent">
                    <div className="tab-pane fade show active mt-4" id="nav-raw" role="tabpanel"
                         aria-labelledby="nav-flux-mqtt">
                        <div className="container main-upload">
                            <div className="d-flex justify-content-between">
                                <button type="button" className="btn btn-primary buttonModel"
                                        onClick={() => this.onChangeModalAdd()}>Ajouter un flux MQTT
                                </button>
                                <ButtonStatus />
                            </div>
                            <div className="main-download">
                                <div className="mt-4">
                                    <div className="data-table">
                                        <TableMqttConfig/>
                                        <ModalAdd/>
                                        <ModalEdit/>
                                        <ModalChangeStatus/>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <ToastContainer/>
            </div>
        )
    }
}

const mapStateToProps = (state) => {
    return {
        nameContainer: state.nameContainer,
        auth: state.auth
    }
}

export default connect(mapStateToProps, null)(MqttConfigList)