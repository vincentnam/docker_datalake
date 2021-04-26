import React from "react";

export class Home extends React.Component {
    render() {
        return(
            <div>
                <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
                    <div class="container-fluid">
                        <a class="navbar-brand" href="/">Datalake</a>
                    <div>
                    </div>
                        <a class="btn btn-outline-primary" href="#" role="button">Déconnexion</a>
                    </div>
                </nav>
                <div class="p-4">
                    <div class="row">
                        <div class="col-sm-4">
                            <div class="card border-dark mb-3">
                                <div class="card-body">
                                    <h5 class="card-title">Data Visualization</h5>
                                    <p class="card-text">Partie data visualization des données brutes et traitées du Datalake.</p>
                                    <a href="/data-visualization" class="btn btn-outline-primary">Accéder</a>
                                </div>
                            </div>
                        </div>
                        <div class="col-sm-4">
                            <div class="card border-dark mb-3">
                                <div class="card-body">
                                    <h5 class="card-title">Download</h5>
                                    <p class="card-text">Partie téléchargement des donnée brutes et traitées du Data Lake.</p>
                                    <a href="/download" class="btn btn-outline-primary">Accéder</a>
                                </div>
                            </div>
                        </div>
                        <div class="col-sm-4">
                            <div class="card border-dark mb-3">
                                <div class="card-body">
                                    <h5 class="card-title">Upload</h5>
                                    <p class="card-text">Partied'envoie de donnée vers le Datalake.</p>
                                    <a href="/upload" class="btn btn-outline-primary">Accéder</a>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        );
    }
}