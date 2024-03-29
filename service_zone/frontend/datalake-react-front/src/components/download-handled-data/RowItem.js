import React from "react";

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
        let beginDate = this.props.beginDate
        let endDate = this.props.endDate
        return (
            <tr>
                <td>
                    <div className="form-check">
                        <input className="form-check-input" onChange={this.handleChange} checked={this.isSelected()}
                            type="checkbox" value="" id="flexCheckDefault"/>
                    </div>
                </td>
                <td>{this.props.item.filename}</td>
                <td>{this.props.item.filesize}</td>
                <td>{beginDate}</td>
                <td>{endDate}</td>
            </tr>
        );
    }
}