import React from "react";
import {DataAnomalyVisiualisation} from './anomaly-data/anomaly-visualisation';
import Filters from "./anomaly-data/Filters";
import {connect} from "react-redux";
import {loadInfoUser} from "../hook/User/User";
import {anomaliesAll} from "../hook/Anomalies/Anomalies";

class DetectionAnomalies extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            dataFilters: [],
            selectMeasurement: "",
            selectTopic: "",
            all_data: [],
            nbr_anomaly: "",
            container_name: this.props.nameContainer.nameContainer
        };
    }

    componentDidMount() {
        if (this.props.nameContainer.nameContainer !== "") {
            this.setState({
                container_name: this.props.nameContainer.nameContainer,
            })
            this.loadData();
        } else {
            this.loadRolesProjectsUser();
        }
    }

    loadRolesProjectsUser() {
        const info = loadInfoUser(localStorage.getItem('token'))
        info.then((response) => {
            this.setState({container_name: response.container_name});
            this.loadData();
        });
    }

    loadData() {
        const anomalies = anomaliesAll(this.props.nameContainer.nameContainer,localStorage.getItem('token'))
        anomalies.then((response) => {
            this.setState({dataFilters: response.dataFilters});
        });
    }


    handleChange(event) {
        const target = event.target;
        const value = target.type === 'checkbox' ? target.checked : target.value;
        const name = target.name;
        this.setState({
            [name]: value,
        });
    }

    handleCallbackData = (childData) => {
        this.setState({dataFilters: childData})
    }
    handleCallbackMeasurement = (childData) => {
        this.setState({selectMeasurement: childData})
    }
    handleCallbackTopic = (childData) => {
        this.setState({selectTopic: childData})
    }

    render() {
        return (
            <div>
                <div className="container main-download mt-4">
                    <Filters
                        data={this.handleCallbackData}
                        selectMeasurement={this.handleCallbackMeasurement}
                        selectTopic={this.handleCallbackTopic}
                    />
                    <DataAnomalyVisiualisation
                        measurement={this.state.selectMeasurement}
                        topic={this.state.selectTopic}
                        data={this.state.dataFilters}
                    />
                </div>
            </div>
        );
    }

}

const mapStateToProps = (state) => {
    return {
        nameContainer: state.nameContainer,
        auth: state.auth
    }
}

export default connect(mapStateToProps, null)(DetectionAnomalies)
