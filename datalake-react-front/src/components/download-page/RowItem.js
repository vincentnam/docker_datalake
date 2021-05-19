import React from "react";
import Moment from 'moment';

export class RowItem extends React.Component {
    checked = false

    constructor(props) {
        super(props);
        this.props = props
    }

    isSelected() {
        let checked = null
        if(this.props.selectedElements) {
            this.props.selectedElements.map(s => {
                if(JSON.stringify(s) == JSON.stringify(this.props.item)) {
                    checked = true
                }
            })
        } 

        return checked
    }

    handleChange = (event) => {
        this.props.handler(this.props.item, event)
    }

    render() {

        return(
            <tr>
                <td scope="row">{ this.props.item.swift_object_id }</td>
                <td>{ this.props.item.swift_container }</td>
                <td>{ this.props.item.content_type }</td>
                <td>{ this.props.item.swift_user }</td>
                <td>{ this.props.item.original_object_name }</td>
                <td>{ Moment(this.props.item.creation_date).format('YYYY-MM-DD hh:mm:ss') }</td>
                <td>
                    <div class="form-check">
                        <input class="form-check-input" onChange={this.handleChange} checked={this.isSelected()} type="checkbox" value="" id="flexCheckDefault" />
                    </div>
                </td>
            </tr>
        );
    }
}