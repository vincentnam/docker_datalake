import React from "react";

export class RowItem extends React.Component {

    constructor(props) {
        super(props);
        this.props = props
        console.log(this.props)
    }

    handleChange = (event) => {
        let selectedElement = { 
            id: this.props.item.id,
            title: this.props.item.title, 
            metadata: this.props.item.metadata
        }
        

        this.props.handler(selectedElement, event)
    }

    render() {
        return(
            <tr>
                <th scope="row">{ this.props.item.id }</th>
                <td>{ this.props.item.title }</td>
                <td>{ this.props.item.metadata }</td>
                <td>
                    <div class="form-check">
                        <input class="form-check-input" onChange={this.handleChange} type="checkbox" value="" id="flexCheckDefault" />
                    </div>
                </td>
            </tr>
        );
    }
}