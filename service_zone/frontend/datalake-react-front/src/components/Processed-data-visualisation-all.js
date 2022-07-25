import React from "react";
//import DataSensors from "./data-sensors/DataSensors";
//import DataSGE from "./data-SGE/DataSGE";
//import DownloadRaw from "./download-raw-data/DownloadRaw";
//import DownloadHandleData from "./download-handled-data/DownloadHandleData";
import { ToastContainer } from 'react-toastify';
//import {ProcessedDataVisualisationTimeSeries} from './Processed-data-visualisation-time-series';
import {ProcessedDataSensors} from './data-sensors/Processd-data-sensors';
import {ProcessedDataSGE} from './data-SGE/Processd-data-SGE';


export class ProcessedDataVisualisationAll extends React.Component {
    render() {
        return (
            <div>
                <div className="container main-download">
                    <nav className="tab-download">
                        <div className="nav nav-pills " id="pills-tab" role="tablist">
                            <button className="nav-link active" id="nav-raw-tab" data-bs-toggle="pill"
                                    data-bs-target="#nav-raw" type="button" role="tab" aria-controls="nav-raw"
                                    aria-selected="true">Données capteurs
                            </button>
                            <button className="nav-link" id="nav-handled-tab" data-bs-toggle="pill"
                                    data-bs-target="#nav-handled" type="button" role="tab" aria-controls="nav-handled"
                                    aria-selected="false">Données SGE
                            </button>
                        </div>
                    </nav>
                    <div className="tab-content" id="pills-tabContent">
                        <div className="tab-pane fade show active" id="nav-raw" role="tabpanel"
                            aria-labelledby="nav-raw-tab">
                            <ProcessedDataSensors/>
                        </div>
                        <div className="tab-pane fade" id="nav-handled" role="tabpanel"
                            aria-labelledby="nav-handled-tab">
                            <ProcessedDataSGE/>
                        </div>
                    </div>
                    <ToastContainer />
                </div>
            </div>
        )
    }
}