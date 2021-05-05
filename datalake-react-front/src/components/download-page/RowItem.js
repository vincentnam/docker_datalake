import React from "react";
import Moment from 'moment';

export class RowItem extends React.Component {

    constructor(props) {
        super(props);
        this.props = props
    }

    handleChange = (event) => {
        let selectedElement = { 
            title: this.props.item.title, 
            metadata: this.props.item.metadata
        }
        

        this.props.handler(selectedElement, event)
    }

    render() {
        return(
            <tr>
                <td scope="row">{ this.props.item.swift_object_id }</td>
                <td>{ this.props.item.swift_user }</td>
                <td>{ this.props.item.original_object_name }</td>
                <td>{ Moment(this.props.item.creation_date).format('YYYY-MM-DD hh:mm:ss') }</td>
                <td>
                    <div class="form-check">
                        <input class="form-check-input" onChange={this.handleChange} type="checkbox" value="" id="flexCheckDefault" />
                    </div>
                </td>
            </tr>
        );
    }
}