import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import reportWebVitals from './reportWebVitals';
import 'bootstrap/dist/css/bootstrap.css';
import 'bootstrap/dist/js/bootstrap.min.js'
import './style.css';
import 'react-toastify/dist/ReactToastify.css';


import {Home} from './components/Home';
import {ProcessedDataVisualisationTimeSeries} from './components/Processed-data-visualisation-time-series';
import {Upload} from './components/Upload';
import {
    BrowserRouter as Router,
    Switch,
    Route
} from 'react-router-dom';
import {Download} from './components/Download';
import {DownloadRaw} from './components/download-raw-data/DownloadRaw';
import {DownloadHandleData} from './components/download-handled-data/DownloadHandleData';
import {Models} from './components/Models';
import {DetectionAnomalies} from './components/DetectionAnomalies';
import {Traceability} from './components/Traceability';
import {Header} from "./components/Header";
import {Provider} from "react-redux";
import {createStore} from "redux";
import { reducer } from "./store";

const store = createStore(reducer);

ReactDOM.render(
    <React.StrictMode>
        <Router>
            <Provider store={store}>
                <Header />
                <Switch>
                    <Route path="/upload">
                        <Upload/>
                    </Route>
                    <Route path="/download">
                        <Download/>
                    </Route>
                    <Route path="/download-raw">
                        <DownloadRaw/>
                    </Route>
                    <Route path="/download-handled-data">
                        <DownloadHandleData/>
                    </Route>
                    <Route path="/data-processed-visualization">
                        <ProcessedDataVisualisationTimeSeries/>
                    </Route>
                    <Route path="/models">
                        <Models/>
                    </Route>
                    <Route path="/detection-anomalies">
                        <DetectionAnomalies/>
                    </Route>
                    <Route path="/traceability">
                        <Traceability/>
                    </Route>
                    <Route path="/">
                        <Home/>
                    </Route>
                </Switch>
            </Provider>
        </Router>
    </React.StrictMode>,
    document.getElementById('root')
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
