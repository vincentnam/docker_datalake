import React from "react";
import api from '../api/api';
import Moment from 'moment';
import { ProgressBar } from 'react-bootstrap';
import {connect} from "react-redux";

class Traceability extends React.Component {
    constructor(props) {
        super(props);
        // Set some state
        this.state = {
            elements: [],
            offset: 0,
            perPage: 10,
            sort_value: 1,
            sort_field: ''
        };
        this.loadTraceability = this.loadTraceability.bind(this)
    }

    componentDidMount() {
        this.loadTraceability();
        this.timerID = setInterval(
            () => this.loadTraceability(),
            5000
        );
    }

    componentWillUnmount() {
        clearInterval(this.timerID);
    }

    loadTraceability() {
        api.post('uploadssh', {
            container_name: this.props.nameContainer.nameContainer,
            token: localStorage.getItem('token')
        })
            .then((response) => {
                this.setState({
                    elements: response.data.file_upload
                });
            })
            .catch(function (error) {
                console.log(error);
            });
    }
    render() {
        const TableInProgress = () => {
            let dataTableInProgress = "";
            if (this.state.elements.length === 0) {
                dataTableInProgress = (
                    <tr>
                        <td colSpan="5" align="center"><p>Il n'y a aucun fichier qui est en cours d'upload !</p></td>
                    </tr>
                );
            }
            if (this.state.elements.length !== 0) {
                let dataInProgress = [];
                this.state.elements.forEach((element) => {
                    if (element.total_bytes_download !== element.total_bytes) {
                        dataInProgress.push(element);
                    }
                });
                if (dataInProgress.length === 0) {
                    dataTableInProgress = (
                        <tr>
                            <td colSpan="5" align="center"><p>Il n'y a aucun fichier qui est en cours d'upload !</p></td>
                        </tr>
                    );
                } else {
                    dataTableInProgress = dataInProgress.map((element) => (
                        <tr>
                            <td>{element.filename}</td>
                            <td>{element.type_file}</td>
                            <td>
                                <ProgressBar now={(element.total_bytes_download / element.total_bytes) * 100} label={`${Math.round((element.total_bytes_download / element.total_bytes) * 100)}%`} />
                            </td>
                            <td>{Moment(element.created_at).format('DD/MM/YYYY HH:mm:ss')}</td>
                            <td>{Moment(element.update_at).format('DD/MM/YYYY HH:mm:ss')}</td>
                        </tr>
                    ));
                }
                
            }
            return (
                <table className="table table-traceability table-striped table-responsive" id="TableInProgress">
                    <thead>
                        <tr style={{ color: '#ea973b' }}>
                            <th>Nom du fichier</th>
                            <th>Type du fichier</th>
                            <th>Progression de l'upload</th>
                            <th>Début de l'upload</th>
                            <th>Time of control</th>
                        </tr>
                    </thead>
                    <tbody>
                        {dataTableInProgress}
                    </tbody>
                </table>
            )
        }

        const TableFinished = () => {
            let dataTableFinished = "";
            if (this.state.elements.length === 0) {
                dataTableFinished = (
                    <tr>
                        <td colSpan="5" align="center"><p>Il n'y a aucun fichier qui est en upload terminé !</p></td>
                    </tr>

                );
            }
            if (this.state.elements.length !== 0) {
                let dataFinished = [];
                this.state.elements.forEach((element) => {
                    if (element.total_bytes_download === element.total_bytes) {
                        dataFinished.push(element);
                    }
                });
                dataTableFinished = dataFinished.map((element) => (
                    <tr>
                        <td>{element.filename}</td>
                        <td>{element.type_file}</td>
                        <td>
                            <b style={{ color: '#ea973b' }}>Terminé</b>
                        </td>
                        <td>{Moment(element.created_at).format('DD/MM/YYYY HH:mm:ss')}</td>
                        <td>{Moment(element.update_at).format('DD/MM/YYYY HH:mm:ss')}</td>
                    </tr>
                ));
            }
            return (
                <table className="table table-traceability table-striped table-responsive" id="TableFinished">
                    <thead>
                        <tr style={{ color: '#ea973b' }}>
                            <th>Nom du fichier</th>
                            <th>Type du fichier</th>
                            <th>Progression de l'upload</th>
                            <th>Début de l'upload</th>
                            <th>Time of control</th>
                        </tr>
                    </thead>
                    <tbody>
                        {dataTableFinished}
                    </tbody>
                </table>
            )
        }
        return (
            <div>
                <div className="container main-upload">
                    <div className="title">Traçabilité des fichiers upload :</div>
                    <div className="main-download">
                        <nav className="tab-download">
                            <div className="nav nav-pills " id="pills-tab" role="tablist">
                                <button className="nav-link active" id="nav-in-progress-tab" data-bs-toggle="pill"
                                    data-bs-target="#nav-in-progress" type="button" role="tab" aria-controls="nav-small-file"
                                    aria-selected="true">En cours d'upload
                                </button>
                                <button className="nav-link" id="nav-finished-tab" data-bs-toggle="pill"
                                    data-bs-target="#nav-finished" type="button" role="tab" aria-controls="nav-large-file"
                                    aria-selected="false">Upload terminé
                                </button>
                            </div>
                        </nav>
                        <div className="tab-content" id="pills-tabContent">
                            <div className="tab-pane fade show active" id="nav-in-progress" role="tabpanel"
                                aria-labelledby="nav-in-progress-tab">
                                <div className="mt-4">
                                    <div className="data-table">
                                        <TableInProgress />
                                    </div>
                                </div>
                            </div>
                            <div className="tab-pane fade mb-4" id="nav-finished" role="tabpanel"
                                aria-labelledby="nav-finished-tab">
                                <div className="mt-4">
                                    <div className="data-table">
                                        <TableFinished />
                                    </div>
                                </div>
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
        auth: state.auth
    }
}

export default connect(mapStateToProps, null)(Traceability)