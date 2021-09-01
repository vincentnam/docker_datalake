import React from "react";
import {Header} from './Header';
import {DownloadRaw} from "./download-raw-data/DownloadRaw";
import {DownloadHandleData} from "./download-handled-data/DownloadHandleData";

export class Download extends React.Component {
    render() {
        return (
            <div>
                <Header/>
                <div className="container main-download">
                    <nav className="tab-download">
                        <div className="nav nav-pills " id="pills-tab" role="tablist">
                            <button className="nav-link active" id="nav-raw-tab" data-bs-toggle="pill"
                                    data-bs-target="#nav-raw" type="button" role="tab" aria-controls="nav-raw"
                                    aria-selected="true">Données brutes
                            </button>
                            <button className="nav-link" id="nav-handled-tab" data-bs-toggle="pill"
                                    data-bs-target="#nav-handled" type="button" role="tab" aria-controls="nav-handled"
                                    aria-selected="false">Données traitées
                            </button>
                        </div>
                    </nav>
                    <div className="tab-content" id="pills-tabContent">
                        <div className="tab-pane fade show active" id="nav-raw" role="tabpanel"
                             aria-labelledby="nav-raw-tab">
                            <DownloadRaw/>
                        </div>
                        <div className="tab-pane fade" id="nav-handled" role="tabpanel"
                             aria-labelledby="nav-handled-tab">
                            <DownloadHandleData/>
                        </div>
                    </div>
                </div>
            </div>
        )
    }
}