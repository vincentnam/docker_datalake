import React from "react";
import { FormGroup, FormLabel, Form, Button } from "react-bootstrap";

export class MetadonneesForm extends React.Component {
    constructor(props) {
        super(props);
        this.handleChange = this.handleChange.bind(this);
    }
    handleClick = () => {
        this.props.onDeleteMeta(this.props.value);
    };
    handleChange = (event) => {
        this.props.onHandleChange(event, this.props.value);
    };

    render() {
        return (
            <div className="card col-sm-5 mt-2 mb-2 pb-2 pt-2" key={this.props.value}>
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
                    ></Form.Control>
                </FormGroup>
                <FormGroup>
                    <FormLabel>Type de champs</FormLabel>
                    <Form.Control
                        name="type"
                        as="select"
                        aria-label="Label de la métadonnée"
                        value={this.props.meta.type}
                        onChange={this.handleChange}
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
                    />
                </FormGroup>
            </div>
        );
    }
}