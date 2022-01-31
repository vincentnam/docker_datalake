import React from "react";
import api from '../../api/api';
import $ from 'jquery';
import {Filters} from "./Filters";
import moment from "moment";
import {Paginate} from "./Paginate";
import {LoadingSpinner} from "../utils/LoadingSpinner";
import { toast } from 'react-toastify';
import DataTable from 'react-data-table-component';
import Moment from 'moment';
import {connect} from "react-redux";

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
                id: 'other_data',
                name: "Métadescriptions",
                selector: row => row.other_data ? JSON.stringify(row.other_data) : '-' 
            },
            {
                id: 'creation_date',
                name: "Date de création",
                selector: row => Moment(row.creation_date).format('YYYY-MM-DD HH:mm:ss'),
                sortable: true
            },
        ];

class DownloadRaw extends React.Component {
    url = process.env.REACT_APP_SERVER_NAME
    title = 'Affichage des données brutes'
    selectedElementsOnActualPage = []

    constructor(props) {
        super(props);

        // Bind the this context to the handler function
        this.handler = this.handler.bind(this);
        this.validate = this.validate.bind(this)
        this.setFiletype = this.setFiletype.bind(this);
        this.setBeginDate = this.setBeginDate.bind(this);
        this.setEndDate = this.setEndDate.bind(this);
        this.validateFilters = this.validateFilters.bind(this)
        this.handleShow = this.handleShow.bind(this);
        this.handleClose = this.handleClose.bind(this);
        this.isSelected = this.isSelected.bind(this);

        // Set some state
        this.state = {
            selectedElements: [],
            elements: [],
            offset: 0,
            filetype: '',
            beginDate: moment().format('Y-MM-DD'),
            endDate: moment().format('Y-MM-DD'),
            loading: false,
            perPage: 10,
            sort_value: 1,
            sort_field: ''
        };
    }

    getSelectedElements() {
        return this.state.selectedElements;
    }

    isSelected(row) {
        let checked = null
        let selectedElements = this.state.selectedElements
        if (selectedElements) {
            selectedElements.forEach(s => {
                if (JSON.stringify(s) === JSON.stringify(row)) {
                    this.selectedElementsOnActualPage.push(s)
                    checked = true
                }
            })
        }

        return checked
    }

    handler(event) {
        // selected elements on all pages
        let selectedElements = this.getSelectedElements()

        let selectedElementsTemp = selectedElements

        // selected elements on actual page (component React DataTable send selected elements only on actual page)

        // in actual page, if elements have been selected, add selected ones into selected elements global array
        if(event.selectedRows !== undefined) {
            // loop into selected rows in actual page
            event.selectedRows.forEach((element) => {
                // if selected rows in actual page are not in global selected elements
                if(!this.selectedElementsOnActualPage.includes(element) && !selectedElements.includes(element)){
                    selectedElements.push(element)
                } 
            })

            selectedElements.forEach((selectedElement) => {
                // for deleting one row
                if(!event.selectedRows.includes(selectedElement) && this.selectedElementsOnActualPage.includes(selectedElement)){

                    var index = selectedElements.indexOf(selectedElement)
                    if(index !== -1) {
                        selectedElementsTemp.splice(index, 1)
                    }
                }
            })
        }

        this.setState({
            selectedElements: selectedElementsTemp
        })
    }

    validate() {
        let selectedElements = this.getSelectedElements()
        let body = []
        selectedElements.forEach(element => {
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
                    toast.success("Le téléchargement a été effectué avec succès !", {
                        theme: "colored",
                        position: "top-right",
                        autoClose: 3000,
                        hideProgressBar: false,
                        closeOnClick: true,
                        pauseOnHover: true,
                        draggable: true,
                        progress: undefined,
                    });
                })
                .catch(function (error, status) {
                    console.error(status, error.toString()); // eslint-disable-line
                }).finally(function () {
                this.handleClose()
            }.bind(this))

            // empty selected elements
            this.emptySelectedlements()
            this.loadObjectsFromServer()
        } else {
            alert('Veuillez sélectionner une métadonnée !')
        }
    }

    handleClose() {
        this.setState({
            loading: false
        })
    }

    handleShow() {
        this.setState({
            loading: true
        })
    }

    emptySelectedlements() {
        this.setState({
            selectedElements: []
        })
    }

    componentDidMount() {
        this.loadObjectsFromServer();
    }

    handlePageClick = (data) => {
        this.selectedElementsOnActualPage = []
        let selected = data.selected;
        let offset = Math.ceil(selected * this.state.perPage);

        this.setState({offset: offset}, () => {
            this.loadObjectsFromServer();
        });
    };

    handleChangePerPage = (event) => {
        let selectedPerPage = parseInt(event.target.value);
        this.setState({perPage: selectedPerPage}, () => {
            this.loadObjectsFromServer();
        });
    };

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
                sort_value: this.state.sort_value,
                container_name: this.props.nameContainer.nameContainer
            })
        } else {
            data = JSON.stringify({
                limit: this.state.perPage,
                offset: this.state.offset,
                filetype: this.state.filetype,
                beginDate: this.state.beginDate,
                endDate: this.state.endDate,
                container_name: this.props.nameContainer.nameContainer
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

    setFiletype(value) {
        let filetype = value;
        return this.setState({filetype: filetype})
    }

    setBeginDate(value) {
        let beginDate = value;
        return this.setState({beginDate: beginDate})
    }

    setEndDate(value) {
        let endDate = value;
        return this.setState({endDate: endDate})
    }

    validateFilters() {
        this.emptySelectedlements()
        this.setState({
            offset: 0
        }, () => {
            this.loadObjectsFromServer();
        })
    }

    render() { 

        let elts = []
        if (this.state.elements) {
            elts = this.state.elements
        }
        let setFiletype = this.setFiletype
        let setBeginDate = this.setBeginDate
        let setEndDate = this.setEndDate
        let validateFilters = this.validateFilters
        let filterData = {
            'filetype': this.state.filetype,
            'beginDate': this.state.beginDate,
            'endDate': this.state.endDate
        }
        //let loading = this.state.loading

        // sort columns
        const handleSort = async (column, sortDirection) => {
            /// reach out to some API and get new data using or sortField and sortDirection
            this.emptySelectedlements()
        
            console.log(column)
            console.log(sortDirection)
            // for desc
            let sort = 1
            if(this.state.sort_value === 1) {
                sort = -1
            }
            this.setState({
                sort_field: column.id,
                sort_value: sort
            }, () => {
                this.loadObjectsFromServer();
            })
        };

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

        return (
            <div>
                <Filters
                    setFiletype={setFiletype}
                    setBeginDate={setBeginDate}
                    setEndDate={setEndDate}
                    validateFilters={validateFilters}
                    data={filterData}
                    title={this.title}
                />
                <div className="download-detail">
                    <div className="row">
                        <div className="col text-left">Résultats trouvés <span>{this.state.totalLength}</span></div>
                        <div className="col text-end per-page">
                            <label>Items par page</label>
                            <select id="per-page-sel" onChange={this.handleChangePerPage}>
                                <option value="5">5</option>
                                <option value="10" selected>10</option>
                                <option value="20">20</option>
                            </select>
                        </div>
                    </div>
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
                        <Paginate
                            elts={elts}
                            handlePageClick={this.handlePageClick}
                            selected={this.state.selected}
                            pageCount={this.state.pageCount}
                        />
                    </div>
                </div>
                <LoadingSpinner loading={this.state.loading}/>
            </div>
        );
    }
}

const mapStateToProps = (state) => {
    return {
        nameContainer: state.nameContainer,
    }
}

export default connect(mapStateToProps, null)(DownloadRaw)