import React from "react";
import { Plot, newTable } from '@influxdata/giraffe';
import moment from 'moment';

export class Graph extends React.Component {
    constructor(props) {
        super(props);
        this.props = props
    }
    times() {
        const times = this.props.dataGraph._time;
        const result = [];
        if (times !== undefined) {
            for (const [key, value] of Object.entries(times)) {
                result.push(value);
            }
        }
        return result;
    }

    values(){
        const values = this.props.dataGraph._value;
        const result = [];
        if (values !== undefined) {
            for (const [key, value] of Object.entries(values)) {
                result.push(value);
            }
        }
        return result;
    }

    measurements() {
        const measurements = this.props.dataGraph._measurement;
        const result = [];
        if (measurements !== undefined) {
            for (const [key, value] of Object.entries(measurements)) {
                result.push(value);
            }
        }
        return result;
    }
    topics() {
        const topics = this.props.dataGraph.topic;
        const result = [];
        if (topics !== undefined) {
            for (const [key, value] of Object.entries(topics)) {
                result.push(value);
            }
        }
        return result;
    }


    numberData(){
        let data = this.props.dataGraph._value;
        let result = null
        if(data === undefined){
            result = 0;
        } else {
            result = Object.keys(this.props.dataGraph._value).length;
        }
        return result;
    }

    render() {

        const style = {
            width: "100%",
            height: "calc(40vh - 0px)",
            margin: "",
        };

        const lineLayer = {
            type: "line",
            x: "_time",
            y: "_value",
            fill: ["_measurement", "topic"],
            lineWidth: 2,
            colors: ['cyan'],
            
        };

        const table = newTable(this.numberData())
            .addColumn('_time', 'dateTime:RFC3339', 'time', this.times())
            .addColumn('_value', 'double', 'number', this.values())
            .addColumn('_measurement', '255', 'string', this.measurements())
            .addColumn('topic', '255', 'string', this.topics());

        const config = {
            table,
            layers: [lineLayer],
            valueFormatters: {
                _time: (t) => moment(new Date(t)).format('DD/MM/YYYY HH:mm'),
            }
        };
        return (
            <div style={style}>
                <Plot config={config} />
            </div>
        );
    }
}