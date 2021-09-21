import React from "react";
import { FormGroup, FormLabel, Form, Button } from "react-bootstrap";

export class MetadonneesForm extends React.Component {
    constructor(props) {
        super(props);
        this.handleChange = this.handleChange.bind(this);
    }
    handleClick = () => {
        this.props.onDeleteMeta(this.props.meta.id);
    };
    handleChange = (event) => {
        const name = event.target.name;
        this.props.meta[name] = event.target.value;
        this.props.onHandleChange(this.props.meta, this.props.value -1);
    };

    render() {
        return (
            <div className="card col-sm-5 mt-2 mb-2 pb-2 pt-2" key={this.props.meta.id}>
                <h6 className="d-flex justify-content-between">Métadonnée n°{this.props.value}
                    <Button className="btn btn-sm btn-danger" onClick={this.handleClick}>Supprimer</Button>
                </h6>
                <FormGroup>
                    <FormLabel>Label</FormLabel>
                    <Form.Control
                        name="label"
                        type="text"
                        placeholder="Label de la métadonnée"
                        value={this.props.meta.label}
                        onChange={this.handleChange}
                        key={`label-${this.props.value}`}
                    ></Form.Control>
                </FormGroup>
                <FormGroup>
                    <FormLabel>Type de champs</FormLabel>
                    <Form.Control
                        name="type"
                        as="select"
                        aria-label="Types de fichiers"
                        value={this.props.meta.type}
                        onChange={this.handleChange}
                        key={`type-${this.props.value}`}
                    >
                        <option>Veuillez choisir le type de champs</option>
                        <option value="text">Text</option>
                        <option value="number">Number</option>
                        <option value="textarea">Textareas</option>
                    </Form.Control>
                </FormGroup>
                <FormGroup>
                    <FormLabel>Name</FormLabel>
                    <Form.Control
                        name="name"
                        type="text"
                        placeholder="Name de la métadonnée"
                        value={this.props.meta.name}
                        onChange={this.handleChange}
                        key={`name-${this.props.value}`}
                    />
                </FormGroup>
            </div>
        );
    }
}