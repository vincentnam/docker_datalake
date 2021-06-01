import React from "react";

export class InputMeta extends React.Component {
    constructor(props) {
        super(props);
        this.props = props

        this.editMeta = this.editMeta.bind(this)
    }

    editMeta(event) {
        console.log("test");
        
        if(event !== undefined && event.target !== undefined) {
            console.log(event)
            const other = this.props.othermeta;
            console.log(other)
            const value = event.target.value
            other[this.props.index].value = value;
            console.log(other)
            this.setState({
                othermeta: other
            });
        }
        
    }

    render() {
        return (
            <div key={this.props.meta.name} class="mb-3">
                <label class="form-label">{this.props.meta.label}</label>
                <input value={this.props.meta.value} onChange={(event) => this.editMeta(event)} type={this.props.meta.type} name={this.props.meta.name} class="form-control" />
            </div>
        )
    }
}