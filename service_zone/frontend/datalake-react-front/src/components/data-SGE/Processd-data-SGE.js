import React from "react";
import Filters from './Filters';
import { DataSGE } from './DataSGE';

export class ProcessedDataSGE extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            dataFilters: [],
            dataGraph : {},
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
    handleCallbackMeasurement = (childData) =>{
        this.setState({selectMeasurement: childData})
    }
    handleCallbackTopic = (childData) =>{
        this.setState({selectTopic: childData})
    }
    
    render() {
        return (
            <div>
                <div className="container main-download mt-5">
                    <Filters
                        data={this.handleCallbackData} 
                        dataGraph={this.handleCallbackDataGraph}
                        selectMeasurement={this.handleCallbackMeasurement}
                        selectTopic={this.handleCallbackTopic}
                    />
                    <DataSGE
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