import React from "react";

export class Header extends React.Component {
    render() {
        return(
            <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
                <div class="container-fluid">
                    <a class="navbar-brand" href="/">Datalake</a>
                    <div class="collapse navbar-collapse" id="navbarText">
                        <ul class="navbar-nav me-auto mb-2 mb-lg-0">
                            <li class="nav-item">
                                <a class="nav-link active" aria-current="page" href="/">Retour</a>
                            </li>
                        </ul>
                    </div>
                </div>
                <div>
                    <a class="btn btn-outline-primary" href="/logout" role="button">Déconnexion</a>
                </div>
            </nav>
        );
    }
}