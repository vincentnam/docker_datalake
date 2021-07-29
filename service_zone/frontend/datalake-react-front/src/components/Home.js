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
                        <a class="btn btn-outline-primary" href="/logout" role="button">Logout</a>
                    </div>
                </nav>
                <div class="p-4">
                    <div class="row">
                        <div class="col-sm-4">
                            <div class="card border-dark mb-3">
                                <div class="card-body">
                                    <h5 class="card-title">Download Raw Data</h5>
                                    <p class="card-text">Téléchargement des données brutes du Datalake.</p>
                                    <a href="/download" class="btn btn-outline-primary">Accéder</a>
                                </div>
                            </div>
                        </div>
                        <div class="col-sm-4">
                            <div class="card border-dark mb-3">
                                <div class="card-body">
                                    <h5 class="card-title">Upload</h5>
                                    <p class="card-text">Envoi des données vers le Datalake.</p>
                                    <a href="/upload" class="btn btn-outline-primary">Accéder</a>
                                </div>
                            </div>
                        </div>
                        <div class="col-sm-4">
                            <div class="card border-dark mb-3">
                                <div class="card-body">
                                    <h5 class="card-title">Datavisualisation data processed Time Series</h5>
                                    <p class="card-text">Partie visualisation des données traitées time series.</p>
                                    <a href="/data-processed-visualisation-time-series" class="btn btn-outline-primary">Accéder</a>
                                </div>
                            </div>
                        </div>
                        <div class="col-sm-4">
                            <div class="card border-dark mb-3">
                                <div class="card-body">
                                    <h5 class="card-title">Download Processed Data</h5>
                                    <p class="card-text">Téléchargement des données traitées du Datalake.</p>
                                    <a href="/download-handled-data" class="btn btn-outline-primary">Accéder</a>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        );
    }
}