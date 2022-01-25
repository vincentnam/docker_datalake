import React from "react";
import { DataAnomalyVisiualisation } from './anomaly-data/anomaly-visualisation';
import { Filters } from "./anomaly-data/Filters";
import api from '../api/api';

export class DetectionAnomalies extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            dataFilters: [],
            selectMeasurement: "",
            selectTopic: "",
            all_data : [],
            nbr_anomaly : ""
        };
    }
    componentDidMount(){
        this.loadData();
    }
    loadData() {
        api.get('getDataAnomalyAll')
            .then((response) => {
                let result = [];
                for (const value of Object.entries(response.data.anomaly.objects)) {
                    result.push(value[1]);
                }
                let all_data = []
                result.forEach((dt) => {
                    //console.log(dt)
                    all_data.push({
                        _id: dt._id,
                        _topic: dt.topic,
                        _value: dt.value,
                        _unit: dt.unit,
                        _datetime : dt.datetime,
                        _startDate_detection: dt.startDate_detection,
                        _endDate_detection: dt.endDate_detection,
                    })
                });
                this.setState({
                    dataFilters: all_data
                });

            })
            .catch(function (error) {
                console.log(error);
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
    handleCallbackData = (childData) =>{
        this.setState({dataFilters: childData})
    }
    handleCallbackMeasurement = (childData) =>{
        this.setState({selectMeasurement: childData})
    }
    handleCallbackTopic = (childData) =>{
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
