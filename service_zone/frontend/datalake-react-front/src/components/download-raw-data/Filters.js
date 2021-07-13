import React from "react";
import { FormGroup, FormLabel, Form, Button } from "react-bootstrap";
import { config } from '../../configmeta/config';

export class Filters extends React.Component {

    constructor(props) {
        super(props);
        this.props = props
        this.validateFilters = this.validateFilters.bind(this);

        this.setFiletype = this.setFiletype.bind(this);
        this.setDatatype = this.setDatatype.bind(this);
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

    // retrieve filetype by id in conf file
    getFiletypeById(datatypeConf, id) {
        let filetypesResult = ""

        datatypeConf.map((type) => (
            // loop in config file
            type.map((t) => {
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

        let filetypesResult = this.getFiletypeById( [config.types], value)
        this.props.setFiletype(filetypesResult) 

        this.setState({
            [name]: value
        });
    }

    render() {
        // data type field
        const SelectDatatype = () => {
            const types = [config.types];
            // loop into conf to get all data types
            const listTypes = types.map((type) => (
                type.map((t) => 
                    <option key={t.id} value={t.id}>{t.label}</option>
                )
            ));
            return (
                <select value={this.state.type} onChange={this.handleChange} name="type" className="form-control">
                    {listTypes}
                </select>
            );
        }


        return (
            <div className="p-4">
                <div className="jumbotron">
                    <h2 className="display-4 text-center">Affichage des données brutes</h2>
                    <Form onSubmit={this.validateFilters}>
                        <div className="form-row">
                        <SelectDatatype />
                        <div className="form-group col-md-6">
                            <FormGroup>
                                <FormLabel>Date de début</FormLabel>
                                <Form.Control type="date" name='beginDate' value={this.props.data.beginDate} onChange={this.setBeginDate} required/>
                            </FormGroup>
                        </div>
                        <div className="form-group col-md-6">
                            <FormGroup>
                                <FormLabel>Date de fin</FormLabel>
                                <Form.Control type="date" name='endDate' value={this.props.data.endDate} onChange={this.setEndDate} required/>
                            </FormGroup>
                        </div>

                        <div className="form-group col-md-12 text-center">
                            <Button type="submit" variant="outline-primary">Filtrer</Button>
                        </div>
                        </div>
                    </Form>
                </div>
            </div>
        );
    }
}