import React from "react";

export class Header extends React.Component {
    render() {
        return(
            <nav className="navbar navbar-expand-lg navbar-dark bg-dark">
                <div className="container-fluid">
                    <a className="navbar-brand" href="/">Datalake</a>
                    <div className="collapse navbar-collapse" id="navbarText">
                        <ul className="navbar-nav me-auto mb-2 mb-lg-0">
                            <li className="nav-item">
                                <a className="nav-link active" aria-current="page" href="/">Retour</a>
                            </li>
                        </ul>
                    </div>
                </div>
                <div>
                    <a className="btn btn-outline-primary" href="/logout" role="button">Déconnexion</a>
                </div>
            </nav>
        );
    }
}