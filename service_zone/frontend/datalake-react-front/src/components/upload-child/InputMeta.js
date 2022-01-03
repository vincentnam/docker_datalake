import React from "react";

export class InputMeta extends React.Component {
    constructor(props) {
        super(props);
        this.props = props

        this.editMeta = this.editMeta.bind(this)
    }

    editMeta(event) {
        if (event !== undefined && event.target !== undefined) {
            const other = this.props.othermeta;
            const value = event.target.value
            other[this.props.index].value = value;
            this.setState({
                othermeta: other
            });
        }

    }

    render() {
        return (
            <div key={this.props.meta.name} className="mb-3 col">
                <label className="form-label meta-label">{this.props.meta.label}</label>
                <input value={this.props.meta.value} onChange={(event) => this.editMeta(event)}
                    type={this.props.meta.type} name={this.props.meta.name} className="form-control"
                    placeholder="Saisissez vos métadonnées" />
            </div>
        )
    }
}