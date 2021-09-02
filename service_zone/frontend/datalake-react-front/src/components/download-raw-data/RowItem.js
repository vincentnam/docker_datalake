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
        let selectedElements = this.props.selectedElements
        if (selectedElements) {
            selectedElements.forEach(s => {
                if (JSON.stringify(s) === JSON.stringify(this.props.item)) {
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

        return (
            <tr>
                <td>
                    <div className="form-check">
                        <input className="form-check-input" onChange={this.handleChange} checked={this.isSelected()}
                            type="checkbox" value="" id="flexCheckDefault"/>
                    </div>
                </td>
                <td>{this.props.item.swift_object_id}</td>
                <td>{this.props.item.swift_container}</td>
                <td>{this.props.item.content_type}</td>
                <td>{this.props.item.swift_user}</td>
                <td>{this.props.item.original_object_name}</td>
                <td>{(this.props.item.other_data ? this.props.item.other_data['meta1'] : '-')}</td>
                <td>{(this.props.item.other_data ? this.props.item.other_data['meta2'] : '-')}</td>
                <td>{Moment(this.props.item.creation_date).format('YYYY-MM-DD hh:mm:ss')}</td>

            </tr>
        );
    }
}