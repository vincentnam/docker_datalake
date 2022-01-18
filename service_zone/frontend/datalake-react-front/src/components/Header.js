import React from "react";

import { NavLink } from 'react-router-dom';
import { ToastContainer, toast } from 'react-toastify';
import api from '../api/api';
import history from "./utils/history";

export class Header extends React.Component {

    constructor() {
        super();
        this.state = {
            anomalies: []
        }
    }

    componentDidMount() {
        this.countData();
    }
    countData() {
        api.get('getDataAnomalyAll')
            .then((response) => {
                this.setState({
                    anomalies: response.data.anomaly
                })
            })
            .catch(function (error) {
                console.log(error);
            });
    }
    render() {
        const Navbar = () => (
            <nav className="navbar-nav">
                <NavLink exact
                    activeClassName="active"
                    className="nav-item nav-link"
                    to="/">
                    Home
                </NavLink>
                <NavLink activeClassName="active"
                    className="nav-item nav-link"
                    to="/upload">
                    Upload
                </NavLink>
                <NavLink activeClassName="active"
                    className="nav-item nav-link"
                    to="/traceability">
                    Traçabilité
                </NavLink>
                <NavLink activeClassName="active"
                    className="nav-item nav-link"
                    to="/download">
                    Download
                </NavLink>
                <NavLink activeClassName="active"
                    className="nav-item nav-link"
                    to="/data-processed-visualization">
                    Data Visualization
                </NavLink>
                <NavLink activeClassName="active"
                    className="nav-item nav-link"
                    to="/models">
                    Gestion
                </NavLink>
                <NavLink activeClassName="active"
                    className="nav-item nav-link"
                    to="/detection-anomalies">
                    Anomalies
                    {this.state.anomalies.length > 0 &&
                        <span class="position-absolute translate-small top-0 badge badge-secondary rounded-pill bg-danger" style={{ marginTop: '5px' }}>
                            {this.state.anomalies.length}
                        </span>
                    }

                </NavLink>
            </nav>
        );
        return (
            <nav className="navbar navbar-expand-lg navbar-dark">
                <div className="container">
                    <a className="navbar-brand" href="/"><img src="images/logo-datalake.svg" alt="neOCampus" /></a>
                    <a href="/" className="navbar-brand-text">Datalake</a>
                    <button className="navbar-toggler" type="button" data-bs-toggle="collapse"
                        data-bs-target="#navbarNavAltMarkup" aria-controls="navbarNavAltMarkup"
                        aria-expanded="false"
                        aria-label="Toggle navigation">
                        <span className="navbar-toggler-icon" />
                    </button>
                    <div className="collapse navbar-collapse" id="navbarNavAltMarkup">
                        <Navbar />
                    </div>
                </div>

            </nav>

        );
    }
}