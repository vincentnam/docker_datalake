import React from 'react';
import {Switch, Route} from 'react-router-dom'
import Home from './components/Home';
import ProcessedDataVisualisationAll from './components/Processed-data-visualisation-all';
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
import Similarity from "./components/Similarity";


const RoutesConnect = (props) => {
    if (localStorage.getItem('isNoProject') !== "") {
        if (localStorage.getItem('isNoProject') === "true") {
            return (
                <Route path="/info">
                    <Info/>
                </Route>
            )
        } else {
            return (
                <>
                    <Route path="/upload" component={props => <Upload {...props} />}/>
                    <Route path="/download" component={props => <Download {...props} />}/>
                    <Route path="/data-visualisation-all"
                           component={props => <ProcessedDataVisualisationAll {...props} />}/>
                    <Route path="/models" component={props => <Models {...props} />}/>
                    <Route path="/detection-anomalies" component={props => <DetectionAnomalies {...props} />}/>
                    <Route path="/traceability" component={props => <Traceability {...props} />}/>
                    <Route path="/mqtt-config" component={props => <MqttConfigList {...props} />}/>
                    <Route path="/similarity" component={props => <Similarity {...props} />}/>
                    <Route path="/home" component={props => <Home {...props} />}/>
                    {props.isAdmin === true &&
                        <Route path="/config-users" component={props => <UsersRolesPojectsConfiguration {...props} />}/>
                    }
                </>
            )
        }
    }

}

const Protected = ({isAdmin, nameContainer}) => {
    return (
        <div>
            <UpBar/>
            <div className="row m-0">
                <SideBar/>
                <div className="col-10 mt-content" style={{marginLeft: "16%"}}>
                    <Switch>
                        <RoutesConnect isAdmin={isAdmin} container={nameContainer}/>
                    </Switch>
                </div>
            </div>
        </div>
    )
}

export default Protected;