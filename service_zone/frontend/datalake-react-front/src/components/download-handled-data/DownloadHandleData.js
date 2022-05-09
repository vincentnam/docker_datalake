import React from "react";
import Filters from "../download-raw-data/Filters";
import moment from "moment";
import api from '../../api/api';
import $ from 'jquery';
import {LoadingSpinner} from "../utils/LoadingSpinner";
import {Paginate} from "../download-raw-data/Paginate";
import DataTable from 'react-data-table-component';
import { toast } from 'react-toastify';
import {connect} from "react-redux";

class DownloadHandleData extends React.Component {
    url = process.env.REACT_APP_SERVER_NAME
    selectedElementsOnActualPage = []

    constructor(props) {
        super(props);

        // Bind the this context to the handler function
        this.validate = this.validate.bind(this)
        this.handler = this.handler.bind(this);
        this.setFiletype = this.setFiletype.bind(this);
        this.setBeginDate = this.setBeginDate.bind(this);
        this.setEndDate = this.setEndDate.bind(this);
        this.validateFilters = this.validateFilters.bind(this)
        this.handleShow = this.handleShow.bind(this);
        this.handleClose = this.handleClose.bind(this)

        // Set some state
        this.state = {
            selectedElements: [],
            elements: {},
            offset: 0,
            filetype: '',
            beginDate: moment().format('Y-MM-DD'),
            endDate: moment().format('Y-MM-DD'),
            loading: false,
            perPage: 10
        };
    }

    getSelectedElements() {
        return this.state.selectedElements;
    }

    validate() {
        let selectedElements = this.getSelectedElements()
        let body1 = []
        let json_object = {}
        selectedElements.forEach(element => {
            if (element.filename === "metadonnees-images-mongodb.json") {
                json_object.mongodb_file = true
            }

            if (element.filename === "donnees-serie-temporelle-influxdb.csv") {
                json_object.influxdb_file = true
            }
        })

        json_object.filetype = this.state.filetype.toString()
        json_object.beginDate = this.state.beginDate
        json_object.endDate = this.state.endDate
        json_object.token = this.props.auth.token

        body1.push(json_object)
        var body = JSON.stringify(body1)

        if (selectedElements.length) {
            this.handleShow();
            api.post('handled-data-file', body, {
                responseType: 'arraybuffer',
                container_name: this.props.nameContainer.nameContainer,
                token: this.props.auth.token
            })
                .then(function (result) {
                    console.log(result.data)
                    const url = window.URL.createObjectURL(new Blob([result.data], {type: 'application/zip'}));
                    let link = document.createElement('a');
                    link.href = url;
                    link.setAttribute('download', 'file.zip'); //or any other extension
                    document.body.appendChild(link);
                    link.click();
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

    handler(event) {
        // selected elements on actual page (component React DataTable send selected elements only on actual page)

        // in actual page, if elements have been selected, add selected ones into selected elements global array
        this.setState({
            selectedElements: event.selectedRows
        })
    }

    loadObjectsFromServer() {
        this.handleShow()
        $.ajax({
            url: this.url + '/handled-data-list',
            data: JSON.stringify({
                limit: this.state.perPage,
                offset: this.state.offset,
                filetype: this.state.filetype.toString(),
                beginDate: this.state.beginDate,
                endDate: this.state.endDate,
                container_name: this.props.nameContainer.nameContainer,
                token: this.props.auth.token
            }),
            xhrFields: {
                withCredentials: true
            },
            crossDomain: true,
            contentType: 'application/json; charset=utf-8',
            dataType: 'json',
            type: 'POST',

            success: (data) => {
                if (!data.error) {
                    let resultsData = this.prepareData(data)
                    this.setState({
                        elements: resultsData,
                        totalLength: Object.keys(data).length,
                        pageCount: Math.ceil(Object.keys(data).length / this.state.perPage),
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

    prepareData(data) {
        let elts = []
        $.each(data, function(i, val) {
            val.beginDate = this.state.beginDate
            val.endDate = this.state.endDate
            elts.push(val)
        }.bind(this))

        return elts
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

        const columns = [
            {
                id: 'filename',
                name: "Nom du fichier",
                selector: row => row.filename
            },
            {
                id: 'swift_container',
                name: "Taille (en bytes)",
                selector: row => row.filesize
            },
            {
                id: 'beginDate',
                name: "Date de début",
                selector: row => row.beginDate
            },
            {
                id: 'endDate',
                name: "Date de fin",
                selector: row => row.endDate
            }
        ];

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
                    filterDataType={'processed-data'}
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
                            persistSelectedRowsOnPageChange
                            paginationTotalRows={this.state.totalLength}
                            customStyles={customStyles}
                        />

                        <div className="p-4">
                            {Object.keys(elts).length ?
                                <div className="col-12 text-center">
                                    <button className="btn btn-darkblue" onClick={this.validate} type="submit">
                                        Télécharger
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
        auth: state.auth
    }
}

export default connect(mapStateToProps, null)(DownloadHandleData)