import React, {useEffect} from "react";
import { Header } from './Header';
import api from '../api/api';
import Moment from 'moment';
import {ProgressBar} from 'react-bootstrap';

export class Traceability extends React.Component {
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
    }

    loadTraceability() {
        api.get('uploadssh')
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

        const Table = () => {
            useEffect(() => {
                setTimeout(() => {
                    this.loadTraceability();
                }, 5000);
            });
            let data = "";
            if(this.state.elements.length === 0){
                data = (
                    <tr>
                        <td colspan="5" align="center"><p>Il n'y a aucun fichier qui est en cours d'upload !</p></td>
                    </tr>
                    
                );
            }
            
            if(this.state.elements.length !== 0) {
                data = this.state.elements.map((element) => (
                    <tr>
                        <td>{element.filename}</td>
                        <td>{element.type_file}</td>
                        <td>
                            <ProgressBar now={(element.total_bytes_download / element.total_bytes) * 100} label={`${Math.round((element.total_bytes_download / element.total_bytes) * 100)}%`} />
                        </td>
                        <td>{Moment(element.created_at).format('YYYY-MM-DD hh:mm:ss')}</td>
                        <td>{Moment(element.update_at).format('YYYY-MM-DD hh:mm:ss')}</td>
                    </tr>
                ));
            } 
            return (
                <table className="table table-traceability table-striped table-responsive">
                    <thead>
                        <tr style={{color: '#ea973b'}}>
                            <th>Nom du fichier</th>
                            <th>Type du fichier</th>
                            <th>Progression du téléchargement</th>
                            <th>Début du téléchargement</th>
                            <th>Dernière modification</th>
                        </tr>
                    </thead>
                    <tbody>
                        {data}
                    </tbody>
                </table>
            )
        }
        return (
            <div>
                <Header />
                <div className="container main-upload">
                    <div className="title">Traçabilité des fichiers en cours d'upload :</div>
                    <div className="mt-4">
                        <div className="data-table">
                            <Table />
                        </div>
                    </div>
                </div>
            </div>
        )
    }
}