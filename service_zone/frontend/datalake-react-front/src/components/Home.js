import React from "react";
import { Header } from "./Header";
import '../home.css';
import $ from 'jquery';
import { config } from '../configmeta/config';
import api from '../api/api';
import { config_processed_data } from '../configmeta/config_processed_data';
import { Filters } from "./download-raw-data/Filters";
import {RowItem} from './download-raw-data/RowItem';
import { LoadingSpinner } from "./utils/LoadingSpinner";

export class Home extends React.Component {
    url = process.env.REACT_APP_SERVER_NAME

    constructor(props) {
        super(props);
        this.props = props
        this.handler = this.handler.bind(this);
        this.validateFilters = this.validateFilters.bind(this);
        this.validate = this.validate.bind(this)
        this.render = this.render.bind(this);

        this.setFiletype = this.setFiletype.bind(this);
        this.setBeginDate = this.setBeginDate.bind(this);
        this.setEndDate = this.setEndDate.bind(this);
        this.handleChange = this.handleChange.bind(this);

        this.state = {
            selectedElements: [],
            type: 0,
            offset: 0,
            perPage: 10
        }
    }

    validateFilters() {
        this.setState({
            offset: 0
        }, () => {
            this.loadObjectsFromServer();
        })
    }

    loadObjectsFromServer() {
        this.handleShow()
        $.ajax({
            url: this.url + '/raw-data',
            data: JSON.stringify({
                limit: this.state.perPage,
                offset: this.state.offset,
                filetype: this.state.filetype,
                beginDate: this.state.beginDate,
                endDate: this.state.endDate
            }),
            xhrFields: {
                withCredentials: true
            },
            crossDomain: true,
            contentType: 'application/json; charset=utf-8',
            dataType: 'json',
            type: 'POST',

            success: (data) => {
                if (data.result) {
                    this.setState({
                        elements: data.result.objects,
                        totalLength: data.result.length,
                        pageCount: Math.ceil(data.result.length / this.state.perPage),
                    });
                }
            },

            error: (xhr, status, err) => {
                console.error(this.url, status, err.toString()); // eslint-disable-line
            },

            complete: () => {
                this.handleClose()
            }
        });
    }

    handleShow() {
        this.setState({
            loading: true
        })
    }

    handleClose() {
        this.setState({
            loading: false
        })
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
        this.setFiletype(filetypesResult) 

        this.setState({
            [name]: value
        });
    }

    setFiletype(value) {
        let filetype = value;
        return this.setState({ filetype: filetype })
    }

    setBeginDate(value) {
        let beginDate = value;
        return this.setState({ beginDate: beginDate })
    }

    setEndDate(value) {
        let endDate = value;
        return this.setState({ endDate: endDate })
    }

    getSelectedElements() {
        return this.state.selectedElements;
    }

    emptySelectedlements() {
        this.setState({
            selectedElements: []
        })
    }

    
    handler(selectedElements, event) {
        let selectedElementsTemp = this.getSelectedElements()

        // if checked
        if (event.target.checked) {
            selectedElementsTemp.push(selectedElements)

        } else {
            selectedElementsTemp = selectedElementsTemp.filter((element) => JSON.stringify(element) !== JSON.stringify(selectedElements))
        }

        this.setState({
            selectedElements: selectedElementsTemp
        })
    }

    validate() {
        let selectedElements = this.getSelectedElements()
        let body = []
        selectedElements.map(element => {
            body.push({
                'object_id': element.swift_object_id,
                'container_name': element.swift_container
            })
        })

        if (selectedElements.length) {
            this.handleShow();
            api.post('swift-files', body)
                .then(function (result) {
                    let url = result.data.swift_zip
                    const link = document.createElement('a');
                    link.href = url;

                    link.click();
                    window.URL.revokeObjectURL(url);
                })
                .catch(function (error, status) {
                    console.error(status, error.toString()); // eslint-disable-line
                }).finally(function () {
                this.handleClose()
            }.bind(this))

            // empty selected elements
            this.emptySelectedlements()
        } else {
            alert('Veuillez sélectionner une métadonnée !')
        }
    }


    render() {
         // data type field
         const SelectDatatype = () => {
            let types = [config.types];
            if(this.props.title == "Affichage des données traitées"){
                types = [config_processed_data.types];
            }
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
        let handler = this.handler
        let selectedElements = this.getSelectedElements()
        
        let elts = []
        if (this.state.elements) {
            elts = this.state.elements
        }

        let filterData = {
            'filetype': this.state.filetype,
            'beginDate': this.state.beginDate,
            'endDate': this.state.endDate
        }

        return (
            <div>
                <Header/>
                <div className="container main-download">
                    <div className="title">Home</div>
                    <Filters
                        setFiletype={this.setFiletype}
                        setBeginDate={this.setBeginDate}
                        setEndDate={this.setEndDate}
                        validateFilters={this.validateFilters}
                        data={filterData}
                        title={this.title}
                    />

                    <div className="download-detail">
                        <div className="title">Dernières données brutes uploadées</div>
                        <div className="grid mt5 shadow-sm">
                            <table className="table sortable">
                                <thead>
                                <tr>
                                    <th scope="col"></th>
                                    <th scope="col">Id objet Swift</th>
                                    <th scope="col">Container Swift</th>
                                    <th scope="col">Type de fichier</th>
                                    <th scope="col">Utilisateur Swift</th>
                                    <th scope="col">Nom de l'objet</th>
                                    <th scope="col">Meta 1</th>
                                    <th scope="col">Meta 2</th>
                                    <th scope="col">Date de création</th>
                                </tr>
                                </thead>
                                <tbody>

                                {!elts.length ? <tr>
                                        <td colSpan='7' className="text-center">Pas de données</td>
                                    </tr> :

                                    Object.keys(elts).map(function (key, index) {

                                        return <RowItem key={index} item={elts[key]}
                                                        handler={handler}
                                                        selectedElements={selectedElements}/>

                                    })}

                                </tbody>
                            </table>
                            <div className="p-4">
                                {elts.length ?
                                    <div className="col-12 text-center">
                                        <button className="btn btn-darkblue" onClick={this.validate}
                                                type="submit">Télécharger
                                        </button>
                                    </div>
                                    : ''}
                            </div>
                        </div>
                    </div>
                </div>

                <LoadingSpinner loading={this.state.loading}/>
            </div>
        );
    }
}