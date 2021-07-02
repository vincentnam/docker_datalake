import React from "react";
import { FormGroup, FormLabel, Form, Button } from "react-bootstrap";

export class Filters extends React.Component {
    constructor(props) {
        super(props);
        this.props = props
        this.validateFilters = this.validateFilters.bind(this);

        this.setFiletype = this.setFiletype.bind(this);
        this.setDatatype = this.setDatatype.bind(this);
        this.setBeginDate = this.setBeginDate.bind(this);
        this.setEndDate = this.setEndDate.bind(this);
    }

    validateFilters(event) {
        event.preventDefault()
        this.props.validateFilters()

        /*this.props.setFiletype(this.props.data.filetype)   
        this.props.setBeginDate(this.props.data.beginDate)   
        this.props.setEndDate(this.props.data.endDate)*/
    }

    setFiletype(event) {
        let filetype = event.target.value;
        this.props.setFiletype(filetype)      
    }

    setDatatype(event) {
        let datatype = event.target.value;
        this.props.setDatatype(datatype)      
    }
        
    setBeginDate(event) {
        let beginDate = event.target.value;
        this.props.setBeginDate(beginDate)
    }

    setEndDate(event) {
        let endDate = event.target.value;
        this.props.setEndDate(endDate)
    }

    render() {
        return (
            <div class="p-4">
                <div class="jumbotron">
                    <h2 class="display-4 text-center">Affichage des données brutes</h2>
                    <Form onSubmit={this.validateFilters}>
                        <div class="form-row">
                            <div class="form-group required col-md-6">
                                <label for="inputCity control-label">Type de fichier</label>
                                <Form.Control as="select" custom value={this.props.data.filetype} onChange={this.setFiletype} required>
                                    <option selected value=''>Veuillez sélectionner un type</option>
                                    <option value="application/vnd.ms-excel">CSV</option>
                                    <option value="application/json">JSON</option>
                                    <option value="text/plain">Texte</option>
                                    <option value="image">Images</option>
                                </Form.Control>
                            </div>
                            <div class="form-group col-md-6">
                                <label for="inputCity">Type de donnée</label>
                                <Form.Control as="select" custom value={this.props.data.dataType} onChange={this.setDatatype}>
                                    <option selected value=''>Veuillez sélectionner un type</option>
                                    <option value="neOCampus">neOCampus</option>
                                </Form.Control>
                            </div>
                            <div class="form-group col-md-6">
                                <FormGroup>
                                    <FormLabel>Date de début</FormLabel>
                                    <Form.Control type="date" name='beginDate' value={this.props.data.beginDate} onChange={this.setBeginDate} required/>
                                </FormGroup>
                            </div>
                            <div class="form-group col-md-6">
                                <FormGroup>
                                    <FormLabel>Date de fin</FormLabel>
                                    <Form.Control type="date" name='endDate' value={this.props.data.endDate} onChange={this.setEndDate} required/>
                                </FormGroup>
                            </div>

                            <div class="form-group col-md-12 text-center">
                                <Button type="submit" variant="outline-primary">Filtrer</Button>
                            </div>
                        </div>
                    </Form>
                </div>
            </div>
        );
    }
}