import React from "react";
import Moment from 'moment';
import {ProgressBar} from 'react-bootstrap';
import {connect} from "react-redux";
import {loadListTraceability} from "../hook/Traceability/Traceability";
import {loadInfoUser} from "../hook/User/User";

class Traceability extends React.Component {
    constructor(props) {
        super(props);
        // Set some state
        this.state = {
            traceability: [],
            traceability_finished: [],
            offset: 0,
            perPage: 10,
            sort_value: 1,
            sort_field: '',
            container_name: this.props.nameContainer.nameContainer,
        };
        this.loadTraceability = this.loadTraceability.bind(this)
        this.loadRolesProjectsUser = this.loadRolesProjectsUser.bind(this)
    }

    componentDidMount() {
        if (this.props.nameContainer.nameContainer !== "") {
            this.setState({
                container_name: this.props.nameContainer.nameContainer,
            });
            this.loadTraceability();
        } else {
            this.loadRolesProjectsUser();
        }
        this.timerID = setInterval(
            () => this.loadTraceability(),
            5000
        );

    }

    loadRolesProjectsUser() {
        const info = loadInfoUser(localStorage.getItem('token'))
        info.then((response) => {
            this.setState({container_name: response.container_name});
            this.loadTraceability();
        });
    }

    componentWillUnmount() {
        clearInterval(this.timerID);
    }

    loadTraceability() {
        const list = loadListTraceability(this.props.nameContainer.nameContainer, localStorage.getItem('token'))
        list.then((response) => {
            this.setState({traceability: response.traceability, traceability_finished: response.traceability_finished});
        });
    }

    render() {
        const TableInProgress = () => {
            let dataTableInProgress = "";
            if (this.state.traceability.length === 0) {
                dataTableInProgress = (
                    <tr>
                        <td colSpan="5" align="center"><p>Il n'y a aucun fichier qui est en cours d'upload !</p></td>
                    </tr>
                );
            }
            if (this.state.traceability.length !== 0) {
                if (this.state.traceability.length === 0) {
                    dataTableInProgress = (
                        <tr>
                            <td colSpan="5" align="center" style={{color: "black !important"}}>Il n'y a aucun fichier
                                qui est en cours d'upload !
                            </td>
                        </tr>
                    );
                } else {
                    const EtatSwift = (etatBoolean, totalUpload, totalFile) => {
                        let etat;
                        if (totalUpload === totalFile) {
                            etat = "En cours";
                        } else {
                            etat = "En attente";
                        }
                        return etat;
                    }
                    dataTableInProgress = this.state.traceability.map((element) => (
                        <tr>
                            <td>{element.filename}</td>
                            <td>{element.type_file}</td>
                            <td>
                                <ProgressBar now={(element.total_bytes_download / element.total_bytes) * 100}
                                             label={`${Math.round((element.total_bytes_download / element.total_bytes) * 100)}%`}/>
                            </td>
                            <td><b
                                style={{color: '#ea973b'}}>{EtatSwift(element.upload_swift, element.total_bytes_download, element.total_bytes)}</b>
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
                    <tr style={{color: '#ea973b'}}>
                        <th>Nom du fichier</th>
                        <th>Type du fichier</th>
                        <th>Progression de l'upload sur le serveur</th>
                        <th>Etat de l'ajout sur Openstack Swift</th>
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
            if (this.state.traceability_finished.length === 0) {
                dataTableFinished = (
                    <tr>
                        <td colSpan="5" align="center">Il n'y a aucun fichier qui est en upload terminé !</td>
                    </tr>

                );
            }
            if (this.state.traceability_finished.length !== 0) {
                dataTableFinished = this.state.traceability_finished.map((element) => (
                    <tr>
                        <td>{element.filename}</td>
                        <td>{element.type_file}</td>
                        <td>
                            <b style={{color: '#ea973b'}}>Terminé</b>
                        </td>
                        <td>
                            <b style={{color: '#ea973b'}}>Terminé</b>
                        </td>
                        <td>{Moment(element.created_at).format('DD/MM/YYYY HH:mm:ss')}</td>
                        <td>{Moment(element.update_at).format('DD/MM/YYYY HH:mm:ss')}</td>
                    </tr>
                ));
            }
            return (
                <table className="table table-traceability table-striped table-responsive" id="TableFinished">
                    <thead>
                    <tr style={{color: '#ea973b'}}>
                        <th>Nom du fichier</th>
                        <th>Type du fichier</th>
                        <th>Progression de l'upload sur le serveur</th>
                        <th>Etat de l'ajout sur Openstack Swift</th>
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
                                        data-bs-target="#nav-in-progress" type="button" role="tab"
                                        aria-controls="nav-small-file"
                                        aria-selected="true">En cours d'upload
                                </button>
                                <button className="nav-link" id="nav-finished-tab" data-bs-toggle="pill"
                                        data-bs-target="#nav-finished" type="button" role="tab"
                                        aria-controls="nav-large-file"
                                        aria-selected="false">Upload terminé
                                </button>
                            </div>
                        </nav>
                        <div className="tab-content" id="pills-tabContent">
                            <div className="tab-pane fade show active" id="nav-in-progress" role="tabpanel"
                                 aria-labelledby="nav-in-progress-tab">
                                <div className="mt-4">
                                    <div className="data-table">
                                        <TableInProgress/>
                                    </div>
                                </div>
                            </div>
                            <div className="tab-pane fade mb-4" id="nav-finished" role="tabpanel"
                                 aria-labelledby="nav-finished-tab">
                                <div className="mt-4">
                                    <div className="data-table">
                                        <TableFinished/>
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
    }
}

export default connect(mapStateToProps)(Traceability)