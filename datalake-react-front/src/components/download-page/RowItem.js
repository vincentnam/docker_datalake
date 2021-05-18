import React from "react";
import Moment from 'moment';

export class RowItem extends React.Component {
    checked = false

    constructor(props) {
        super(props);
        this.props = props
    }

    isSelected() {
        if(this.props.selectedElements) {
            if(this.props.selectedElements.includes(this.props.item)){
                return true
            }
        }
    }

    handleChange = (event) => {

        let selectedElement = { 
            swift_object_id: this.props.item.swift_object_id,
            swift_user: this.props.item.swift_user, 
            original_object_name: this.props.item.original_object_name,
            creation_date: this.props.item.creation_date
        }
        

        this.props.handler(selectedElement, event)
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
                        <input class="form-check-input" onChange={this.handleChange} type="checkbox" value="" id="flexCheckDefault" />
                    </div>
                </td>
            </tr>
        );
    }
}