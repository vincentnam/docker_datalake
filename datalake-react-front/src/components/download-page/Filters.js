import React from "react";
import { FormGroup, FormLabel, Form } from "react-bootstrap";

export class Filters extends React.Component {

    render() {
        return (
            <div class="p-4">
                <div class="jumbotron">
                    <h2 class="display-4 text-center">Filtres d'affichage des métadonnées</h2>
                    <form>
                        <div class="form-row">
                            <div class="form-group col-md-4">
                                <label for="inputCity">Type de fichier</label>
                                <Form.Control as="select" custom>
                                    <option selected>Veullez sélectionner un type</option>
                                    <option value="csv">CSV</option>
                                    <option value="json">JSON</option>
                                    <option value="other">Autres</option>
                                </Form.Control>
                            </div>
                            <div class="form-group col-md-4">
                                <FormGroup>
                                    <FormLabel>Date de début</FormLabel>
                                    <Form.Control type="date" name='beginDate' />
                                </FormGroup>;
                            </div>
                            <div class="form-group col-md-4">
                                <FormGroup>
                                    <FormLabel>Date de fin</FormLabel>
                                    <Form.Control type="date" name='endDate' />
                                </FormGroup>;
                            </div>
                        </div>
                    </form>
                </div>
            </div>
        );
    }
}