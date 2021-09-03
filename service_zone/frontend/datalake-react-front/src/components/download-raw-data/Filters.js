import React from "react";
import { FormGroup, FormLabel, Form, Button } from "react-bootstrap";
import { config } from '../../configmeta/config';
import { config_processed_data } from '../../configmeta/config_processed_data';

export class Filters extends React.Component {

    constructor(props) {
        super(props);
        this.props = props
        this.validateFilters = this.validateFilters.bind(this);

        this.setFiletype = this.setFiletype.bind(this);
        this.setBeginDate = this.setBeginDate.bind(this);
        this.setEndDate = this.setEndDate.bind(this);
        this.handleChange = this.handleChange.bind(this);

        this.state = {
            type: 0
        }
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

    setBeginDate(event) {
        let beginDate = event.target.value;
        this.props.setBeginDate(beginDate)
    }

    setEndDate(event) {
        let endDate = event.target.value;
        this.props.setEndDate(endDate)
    }

    // retrieve filetype by id in conf file
    getFiletypeById(datatypeConf, id) {
        let filetypesResult = ""

        datatypeConf.map((type) => (
            // loop in config file
            type.forEach((t) => {
                // if selected data type corresponds with current data type
                if (t.id === parseInt(id)) {
                    filetypesResult = t.type_file_accepted
                }
            })
        ));

        return filetypesResult
    }

    // when data type has changed
    handleChange(event) {
        const target = event.target;
        const value = target.type === 'checkbox' ? target.checked : target.value;
        const name = target.name;

        let filetypesResult = this.getFiletypeById([config.types], value)
        this.props.setFiletype(filetypesResult)

        this.setState({
            [name]: value
        });
    }

    render() {
        // data type field
        const SelectDatatype = () => {
            let types = [config.types];
            if (this.props.title === "Affichage des données traitées") {
                types = [config_processed_data.types];
            }
            // loop into conf to get all data types
            const listTypes = types.map((type) => (
                type.map((t) =>
                    <option key={t.id} value={t.id}>{t.label}</option>
                )
            ));
            return (
                <div className="col-md-3 border-right">
                    <FormLabel>Type de fichier</FormLabel>
                    <select value={this.state.type} onChange={this.handleChange} name="type" className="form-select">
                        {listTypes}
                    </select>
                </div>
            );
        }


        return (
            <div className="jumbotron shadow-sm">
                <Form onSubmit={this.validateFilters}>
                    <div className="row align-items-center">
                        <SelectDatatype />
                        <div className="form-group col-md-3 border-right">
                            <FormGroup>
                                <FormLabel>Date de début</FormLabel>
                                <Form.Control type="date" name='beginDate' value={this.props.data.beginDate}
                                    onChange={this.setBeginDate} required />
                            </FormGroup>
                        </div>
                        <div className="form-group col-md-3">
                            <FormGroup>
                                <FormLabel>Date de fin</FormLabel>
                                <Form.Control type="date" name='endDate' value={this.props.data.endDate}
                                    onChange={this.setEndDate} required />
                            </FormGroup>
                        </div>

                        <div className="form-group col-md-3">
                            <Button type="submit" className="btn-oran btn-search float-end">
                                <img alt="Icon Search" src="/images/icon-search.svg" />
                            </Button>
                        </div>
                    </div>
                </Form>
            </div>
        );
    }
}