import React from "react";
import moment from 'moment';

export class RowItem extends React.Component {

    constructor(props) {
        super(props);
        this.props = props
    }
    render() {
        return(
            <tr>
                <th>{moment.unix(this.props.dt._time / 1000).format("DD/MM/YYYY HH:mm:ss")}</th>
                <td>{this.props.dt._value}</td>
                <td>{this.props.dt._measurement}</td>
                <td>{this.props.dt.topic}</td>
            </tr>
        );
    }
}