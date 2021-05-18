import React from "react";
import { FormGroup, FormLabel, Form, Button } from "react-bootstrap";

export class Filters extends React.Component {
    constructor(props) {
        super(props);
        this.props = props
        this.validateFilters = this.validateFilters.bind(this);

        this.setFiletype = this.setFiletype.bind(this);
        this.setBeginDate = this.setBeginDate.bind(this);
        this.setEndDate = this.setEndDate.bind(this);
    }

    validateFilters() {
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
                    <h2 class="display-4 text-center">Filtres d'affichage des métadonnées</h2>
                    <form>
                        <div class="form-row">
                            <div class="form-group col-md-4">
                                <label for="inputCity">Type de fichier</label>
                                <Form.Control as="select" custom value={this.props.data.filetype} onChange={this.setFiletype}>
                                    <option selected value=''>Veuillez sélectionner un type</option>
                                    <option value="csv">CSV</option>
                                    <option value="json">JSON</option>
                                    <option value="text/plain">Texte</option>
                                </Form.Control>
                            </div>
                            <div class="form-group col-md-4">
                                <label for="inputCity">Type de donnée</label>
                                <Form.Control as="select" custom value={this.props.data.contentType} onChange={this.setContentType}>
                                    <option selected value=''>Veuillez sélectionner un type</option>
                                    <option value="neOCampus">neOCampus</option>
                                </Form.Control>
                            </div>
                            <div class="form-group col-md-4">
                                <FormGroup>
                                    <FormLabel>Date de début</FormLabel>
                                    <Form.Control type="date" name='beginDate' value={this.props.data.beginDate} onChange={this.setBeginDate}/>
                                </FormGroup>
                            </div>
                            <div class="form-group col-md-4">
                                <FormGroup>
                                    <FormLabel>Date de fin</FormLabel>
                                    <Form.Control type="date" name='endDate' value={this.props.data.endDate} onChange={this.setEndDate} />
                                </FormGroup>
                            </div>

                            <div class="form-group col-md-12">
                            <Button variant="outline-primary" onClick={this.validateFilters}>Filtrer</Button>
                            </div>
                        </div>
                    </form>
                </div>
            </div>
        );
    }
}