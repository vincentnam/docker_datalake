import React from "react";
import { Plot, newTable } from '@influxdata/giraffe';
import moment from 'moment';
import { Graph } from './graph';
import { Paginate } from "./Paginate";
import { RowItem } from './RowItem';

export class DataVisiualisation extends React.Component {
    constructor(props) {
        super(props);
        this.props = props;
        this.state = {
            count: 0,
            offset: 0,
            perPage: 10,
            pageCount: Math.ceil(this.props.data.length / this.perPage),
        };
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

    values() {
        const values = this.props.dataGraph._value;
        const result = [];
        if (values !== undefined) {
            for (const [key, value] of Object.entries(values)) {
                result.push(value);
            }
        }
        return result;
    }
    numberData() {
        let data = this.props.dataGraph._value;
        let result = null
        if (data === undefined) {
            result = 0;
        } else {
            result = Object.keys(this.props.dataGraph._value).length;
        }
        return result;
    }
    render() {
        const TitleGraph = () => {
            if (this.props.topic === "") {
                return (
                    <h4>Graphique: </h4>
                );
            } else {
                return (
                    <h4>Graphique: Bucket: {this.props.bucket} avec le Measurement: {this.props.measurement} et le Topic: {this.props.topic}</h4>
                );
            }
        }
        return (
            <div>
                <h2>Data visualisation</h2>
                <TitleGraph />
                <Graph
                    data={this.props.data}
                    dataGraph={this.props.dataGraph}
                />
                <h4 class="mt-4">Tableau des données</h4>
                <table class="table table-bordered table-responsive-sm">
                    <thead class="thead-dark">
                        <tr>
                            <th scope="col">Datetime</th>
                            <th scope="col">Valeur</th>
                            <th scope="col">Measurement</th>
                            <th scope="col">Topic</th>
                        </tr>
                    </thead>
                    <tbody>
                        {!this.props.data.length ? <tr> <td colspan='7' class="text-center">Pas de données</td> </tr> :
                            this.props.data.map((dt) => {
                                return <RowItem
                                    key={this.state.count++}
                                    dt={dt}/>
                            })}
                    </tbody>
                </table>
            </div>
        );
    }
}