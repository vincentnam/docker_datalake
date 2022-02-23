import React from "react";
import api from '../api/api';
import {Button, Modal, ProgressBar} from 'react-bootstrap';
import {connect} from "react-redux";
import ConfigMqttAdd from "./mqtt-config/ConfigMqttAdd";
import ConfigMqttEdit from "./mqtt-config/ConfigMqttEdit";

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
            selectElement: {}
        };
        this.loadMqttConfig = this.loadMqttConfig.bind(this);
        this.onChangeModalAdd = this.onChangeModalAdd.bind(this);
        this.onChangeModalEdit = this.onChangeModalEdit.bind(this);
    }

    componentDidMount() {
        this.loadMqttConfig();
    }

    loadMqttConfig() {
        api.post('mqtt/all', {
            container_name: this.props.nameContainer.nameContainer
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

    render() {
        const TableMqttConfig = () => {
            let dataMqttConfig = "";
            if (this.state.elements.length === 0) {
                dataMqttConfig = (
                    <tr>
                        <td colSpan="5" align="center"><p>Il n'y a aucun fichier qui est en cours d'upload !</p></td>
                    </tr>
                );
            } else {
                const StatusButton = (props) => {
                    const status = props.status;
                    if (status) {
                        return <button type="button" className="btn btn-success">En cours</button>;
                    }
                    return <button type="button" className="btn btn-danger">Arrêter</button>;
                }

                dataMqttConfig = this.state.elements.map((element, index) => (
                    <tr key={index}>
                        <td>{element.name}</td>
                        <td><span className="text-break">{element.description}</span></td>
                        <td>{element.brokerUrl}</td>
                        <td>
                            <button type="button" className="btn btn-primary buttonModel" onClick={() => this.onChangeModalEdit(element)}>Modifier</button>
                        </td>
                        <td>
                            <StatusButton status={element.status}/>
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
                            close={this.onChangeModalEdit}
                            reload={this.loadMqttConfig}
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
                    onHide={() => this.onChangeModalEdit()}
                    aria-labelledby="model-edit"
                >
                    <Modal.Header>
                        <Modal.Title id="model-edit">
                            Modifier un flux MQTT
                        </Modal.Title>
                    </Modal.Header>
                    <Modal.Body>
                        <ConfigMqttEdit
                            containerName={this.props.nameContainer.nameContainer}
                            listElements={this.state.elements}
                            selectElement={this.state.selectElement}
                            close={this.onChangeModalEdit}
                            reload={this.loadMqttConfig}
                        />
                    </Modal.Body>
                </Modal>
            )
        }

        return (
            <div>
                <div className="container main-upload">
                    <div className="title">Liste des différents flux MQTT :</div>
                    <button type="button" className="btn btn-primary buttonModel" onClick={() => this.onChangeModalAdd()}>Créer un modèle</button>
                    <div className="main-download">
                        <div className="mt-4">
                            <div className="data-table">
                                <TableMqttConfig/>
                                <ModalAdd/>
                                <ModalEdit/>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        )
    }
}

const mapStateToProps = (state) => {
    return {
        nameContainer: state.nameContainer,
    }
}

export default connect(mapStateToProps, null)(MqttConfigList)