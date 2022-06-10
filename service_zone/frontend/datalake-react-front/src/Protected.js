import React from 'react';
import {Switch, Route} from 'react-router-dom'
import Home from './components/Home';
import {ProcessedDataVisualisationTimeSeries} from './components/Processed-data-visualisation-time-series';
import Upload from './components/Upload';
import {Download} from './components/Download';
import Models from './components/Models';
import DetectionAnomalies from './components/DetectionAnomalies';
import Traceability from './components/Traceability';
import MqttConfigList from "./components/Mqtt-config-list";
import UsersRolesPojectsConfiguration from "./components/Users-roles-pojects-configuration";
import UpBar from "./components/UpBar";
import SideBar from "./components/SideBar";
import Info from "./components/Info";


const RoutesConnect = (isAdmin) => {
    if (localStorage.getItem('isNoProject') !== "") {
        if(localStorage.getItem('isNoProject') === "true" ) {
            return (
                <Route path="/info">
                    <Info/>
                </Route>
            )
        } else {
            return (
                <>
                    <Route path="/upload">
                        <Upload/>
                    </Route>
                    <Route path="/download">
                        <Download/>
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
                    <Route path="/mqtt-config">
                        <MqttConfigList/>
                    </Route>
                    <Route path="/home">
                        <Home/>
                    </Route>
                    {isAdmin.isAdmin === true &&
                        <Route path="/config-users">
                            <UsersRolesPojectsConfiguration/>
                        </Route>

                    }
                </>
            )
        }
    }

}

const Protected = ({isAdmin}) => {
    return (
        <div>
            <UpBar/>
            <div className="row m-0">
                <SideBar/>
                <div className="col-10 mt-content" style={{marginLeft: "16%"}}>
                    <Switch>
                        <RoutesConnect isAdmin={isAdmin}/>
                    </Switch>
                </div>
            </div>
        </div>
    )
}

export default Protected;