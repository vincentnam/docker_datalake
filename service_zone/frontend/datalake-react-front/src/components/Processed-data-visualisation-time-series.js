import React from "react";
import { Header } from './Header';
import { Filters } from './processed-data/Filters';
import { DataVisiualisation } from './processed-data/data-visualisation';

export class ProcessedDataVisualisationTimeSeries extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            dataFilters: [],
            dataGraph : {},
            selectBucket: "",
            selectMeasurement: "",
            selectTopic: "",
        };
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
    handleCallbackDataGraph = (childData) =>{
        this.setState({dataGraph: childData})
    }
    handleCallbackBucket = (childData) =>{
        this.setState({selectBucket: childData})
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
                <Header />
                <div className="container main-download mt-4">
                    <Filters
                        data={this.handleCallbackData} 
                        dataGraph={this.handleCallbackDataGraph}
                        selectBucket={this.handleCallbackBucket}
                        selectMeasurement={this.handleCallbackMeasurement}
                        selectTopic={this.handleCallbackTopic}
                    />
                    <DataVisiualisation
                        bucket={this.state.selectBucket}
                        measurement={this.state.selectMeasurement}
                        topic={this.state.selectTopic}
                        data={this.state.dataFilters}
                        dataGraph={this.state.dataGraph}
                    />
                </div>
            </div>
        );
    }
}