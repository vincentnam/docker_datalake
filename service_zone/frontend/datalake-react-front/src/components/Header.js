import React from "react";

import { NavLink } from 'react-router-dom';
import { ToastContainer, toast } from 'react-toastify';
import api from '../api/api';
import history from "./utils/history";

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
        </NavLink>
    </nav>
);

export class Header extends React.Component {

    componentDidMount() {
        this.countData();
    }
    countData() {
        api.get('getDataAnomalyAll')
            .then((response) => {
                let result = response.data.anomaly.length;

                if (result !== 0) {
                    this.toastError("Il y a " + result + " anomalies dans les données du Datalake !");
                }
            })
            .catch(function (error) {
                console.log(error);
            });
    }

    toastError(message) {
        toast.error(`${message}`, {
            theme: "colored",
            position: "top-right",
            hideProgressBar: false,
            closeOnClick: true,
            autoClose: false,
            pauseOnHover: true,
            draggable: true,
            progress: undefined,
            onClick: props => {
                history.push('/detection-anomalies')
            },
        });
    }
    render() {
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

                <ToastContainer />
            </nav>

        );
    }
}