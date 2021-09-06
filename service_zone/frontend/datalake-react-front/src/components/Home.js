import React from "react";
import { Header } from "./Header";
import '../home.css';
import $ from 'jquery';
import { config } from '../configmeta/config';
import api from '../api/api';
import { config_processed_data } from '../configmeta/config_processed_data';
import { Filters } from "./download-raw-data/Filters";
import {RowItem} from './download-raw-data/RowItem';
import Moment from "moment";
import DataTable from 'react-data-table-component';
import { LoadingSpinner } from "./utils/LoadingSpinner";

export class Home extends React.Component {
    url = process.env.REACT_APP_SERVER_NAME
    selectedElementsOnActualPage = []

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
        let data = null
        if(this.state.sort_field && this.state.sort_value) {
            data = JSON.stringify({
                limit: this.state.perPage,
                offset: this.state.offset,
                filetype: this.state.filetype,
                beginDate: this.state.beginDate,
                endDate: this.state.endDate,
                sort_field: this.state.sort_field,
                sort_value: this.state.sort_value
            })
        } else {
            data = JSON.stringify({
                limit: this.state.perPage,
                offset: this.state.offset,
                filetype: this.state.filetype,
                beginDate: this.state.beginDate,
                endDate: this.state.endDate
            })
        }

        this.handleShow()
        $.ajax({
            url: this.url + '/raw-data',
            data: data,
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

    
    handler(event) {
        //console.log(event)

        // selected elements on all pages
        let selectedElements = this.getSelectedElements()

        // selected elements on actual page (component React DataTable send selected elements only on actual page)

        // in actual page, if elements have been selected, add selected ones into selected elements global array
        if(event.selectedRows !== undefined) {
            // loop into selected rows in actual page
            event.selectedRows.map((element) => {
                // if selected rowx in actual page is not in global selected elements
                console.log('page actuelle')
                console.log(this.selectedElementsOnActualPage)
                if(!this.selectedElementsOnActualPage.includes(element)){
                    console.log('AJOUTE')
                    //selectedElements.push(element)
                } 
            })
        }

       /* if(this.selectedElementsOnActualPage.length > 0) {
            this.selectedElementsOnActualPage.map((selectedElement) => {
                console.log('SELECTION')
                console.log(event.selectedRows)
                if(!event.selectedRows.includes(selectedElement)) {
                    var index = selectedElements.indexOf(selectedElement)
                    if(index != -1) {
                        console.log('INDEX')
                        console.log(index)
                        selectedElements.splice(index, 1)
                    }
                }
            })
        }*/

        this.setState({
            selectedElements: event.selectedRows
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

         // sort columns
         const handleSort = async (column, sortDirection) => {
            /// reach out to some API and get new data using or sortField and sortDirection
        
            console.log(column)
            console.log(sortDirection)
            // for desc
            let sort = 1
            if(this.state.sort_value == 1) {
                sort = -1
            }
            this.setState({
                sort_field: column.id,
                sort_value: sort
            }, () => {
                this.loadObjectsFromServer();
            })
        };

        let filterData = {
            'filetype': this.state.filetype,
            'beginDate': this.state.beginDate,
            'endDate': this.state.endDate
        }

         //  Internally, customStyles will deep merges your customStyles with the default styling.
         const customStyles = {
            table: {
                style: {
                    padding: '0.5rem 0.5rem',
                    borderBottomWidth: '1px',
                    boxShadow: 'inset 0 0 0 9999px var(--bs-table-accent-bg)',
                    '--bs-table-bg': 'transparent',
                    '--bs-table-accent-bg': 'transparent',
                    '--bs-table-striped-color': '#212529',
                    '--bs-table-striped-bg': 'rgba(0, 0, 0, 0.05)',
                    '--bs-table-active-color': '#212529',
                    '--bs-table-active-bg': 'rgba(0, 0, 0, 0.1)',
                    '--bs-table-hover-color': '#212529',
                    '--bs-table-hover-bg': 'rgba(0, 0, 0, 0.075)',
                    width: '100%',
                    marginBottom: '1rem',
                    color: '#212529',
                    verticalAlign: 'top',
                    borderColor: '#dee2e6',
                    backgroundColor: 'rgba(0, 0, 0, 0.05)'
                }
            },
            rows: {
                style: {
                    minHeight: '72px', // override the row height
                    '&:hover': {
                        cursor: 'pointer',
                        backgroundColor: '#ea973b'
                      },
                },
            },
            headCells: {
                style: {
                    paddingLeft: '8px', // override the cell padding for head cells
                    paddingRight: '8px',
                    color: '#ea973b' ,
                    borderColor: 'inherit',
                    borderStyle: 'solid',
                    borderWidth: '0',
                    borderBottomColor: 'currentColor',
                    backgroundColor: 'rgba(0, 0, 0, 0.05)'

                },
            },
            cells: {
                style: {
                    paddingLeft: '8px', // override the cell padding for data cells
                    paddingRight: '8px'
                },
            },
        };

        const columns = [
            {
                id: 'swift_object_id',
                name: "Id objet Swift",
                selector: row => row.swift_object_id,
                sortable: true,
            },
            {
                id: 'swift_container',
                name: "Container Swift",
                selector: row => row.swift_container
            },
            {
                id: 'content_type',
                name: "Type de fichier",
                selector: row => row.content_type,
                sortable: true,
            },
            {
                id: 'swift_user',
                name: "Utilisateur Swift",
                selector: row => row.swift_user,
                sortable: true,
            },
            {
                id: 'original_object_name',
                name: "Nom de l'objet",
                selector: row => row.original_object_name,
                sortable: true,
            },
            {
                id: 'meta1',
                name: "Meta 1",
                selector: row => row.other_data ? row.other_data['meta1'] : '-'
            },
            {
                id: 'meta2',
                name: "Meta 2",
                selector: row => row.other_data ? row.other_data['meta2'] : '-'
            },
            {
                id: 'creation_date',
                name: "Date de création",
                selector: row => Moment(row.creation_date).format('YYYY-MM-DD hh:mm:ss'),
                sortable: true
            },
        ];

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
                            <DataTable
                                columns={columns}
                                data={elts}
                                selectableRows
                                onSelectedRowsChange={this.handler}
                                selectableRowSelected={this.isSelected}
                                persistSelectedRowsOnPageChange
                                paginationTotalRows={this.state.totalLength}
                                onSort={handleSort}
                                sortServer
                                customStyles={customStyles}
                            />

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