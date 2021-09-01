import React from "react";
import {NavLink} from 'react-router-dom';

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
                 to="/download">
            Download
        </NavLink>
        <NavLink activeClassName="active"
                 className="nav-item nav-link"
                 to="/data-processed-visualization">
            Data Visualization
        </NavLink>
    </nav>
);

export class Header extends React.Component {
    render() {
        return (
            <nav className="navbar navbar-expand-lg navbar-dark">
                <div className="container">
                    <a className="navbar-brand" href="/"><img src="images/logo-datalake.svg" alt="neOCampus"/></a>
                    <a href="/" className="navbar-brand-text">Datalake</a>
                    <button className="navbar-toggler" type="button" data-bs-toggle="collapse"
                            data-bs-target="#navbarNavAltMarkup" aria-controls="navbarNavAltMarkup"
                            aria-expanded="false"
                            aria-label="Toggle navigation">
                        <span className="navbar-toggler-icon"/>
                    </button>
                    <div className="collapse navbar-collapse" id="navbarNavAltMarkup">
                        <Navbar/>
                    </div>
                </div>
            </nav>
        );
    }
}