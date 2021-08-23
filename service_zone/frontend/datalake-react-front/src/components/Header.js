import React from "react";
import logo from '../logo_datalake.png'

export class Header extends React.Component {
    render() {
        return (
            <nav className="navbar navbar-expand-lg navbar-dark">
                <div className="container">
                    <a className="navbar-brand" href="/"><img src={logo}></img></a>
                    <a href="/" className="navbar-brand-text">Datalake</a>
                    <button className="navbar-toggler" type="button" data-toggle="collapse"
                            data-target="#navbarNavAltMarkup" aria-controls="navbarNavAltMarkup"
                            aria-expanded="false"
                            aria-label="Toggle navigation">
                        <span className="navbar-toggler-icon"></span>
                    </button>
                    <div className="collapse navbar-collapse" id="navbarNavAltMarkup">
                        <div className="navbar-nav">
                            <a className="nav-item nav-link " href="/">Home</a>
                            <a className="nav-item nav-link active" href="/upload">Upload</a>
                            <a className="nav-item nav-link" href="/download">Download</a>
                            <a className="nav-item nav-link" href="/data-processed-visualization">
                                Data Visualization
                            </a>
                        </div>
                    </div>
                </div>
            </nav>
        );
    }
}