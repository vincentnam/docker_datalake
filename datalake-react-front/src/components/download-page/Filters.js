import React from "react";
import { FormGroup, FormLabel, Form } from "react-bootstrap";

export class Filters extends React.Component {
    constructor(props) {
        super(props);
        this.props = props
        this.setFiletype = this.setFiletype.bind(this);
        this.setBeginDate = this.setBeginDate.bind(this);
        this.setEndDate = this.setEndDate.bind(this);
    }

    setFiletype(event) {
        let filetype = event.target.value;
        this.props.setFiletype(filetype)      
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
                                    <option selected value=''>Veullez sélectionner un type</option>
                                    <option value="csv">CSV</option>
                                    <option value="json">JSON</option>
                                    <option value="other">Autres</option>
                                </Form.Control>
                            </div>
                            <div class="form-group col-md-4">
                                <FormGroup>
                                    <FormLabel>Date de début</FormLabel>
                                    <Form.Control type="date" name='beginDate' value={this.props.data.beginDate} onChange={this.setBeginDate} />
                                </FormGroup>
                            </div>
                            <div class="form-group col-md-4">
                                <FormGroup>
                                    <FormLabel>Date de fin</FormLabel>
                                    <Form.Control type="date" name='endDate' value={this.props.data.endDate} onChange={this.setEndDate} />
                                </FormGroup>
                            </div>
                        </div>
                    </form>
                </div>
            </div>
        );
    }
}