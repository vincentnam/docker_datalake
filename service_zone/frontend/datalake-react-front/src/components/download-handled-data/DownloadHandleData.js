import React from "react";
import {Filters} from "../download-raw-data/Filters";
import moment from "moment";
import api from '../../api/api';
import $ from 'jquery';
import {RowItem} from "./RowItem";
import {LoadingSpinner} from "../utils/LoadingSpinner";
import {Paginate} from "../download-raw-data/Paginate";

export class DownloadHandleData extends React.Component {
    url = process.env.REACT_APP_SERVER_NAME
    title = 'Affichage des données traitées'

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

        body1.push(json_object)
        var body = JSON.stringify(body1)

        if (selectedElements.length) {
            this.handleShow();
            api.post('handled-data-file', body, {
                responseType: 'arraybuffer'
            })
                .then(function (result) {
                    const url = window.URL.createObjectURL(new Blob([result.data], {type: 'application/zip'}));
                    const link = document.createElement('a');
                    link.href = url;
                    link.setAttribute('download', 'file.zip'); //or any other extension
                    document.body.appendChild(link);
                    link.click();
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

    loadObjectsFromServer() {
        this.handleShow()
        $.ajax({
            url: this.url + '/handled-data-list',
            data: JSON.stringify({
                limit: this.state.perPage,
                offset: this.state.offset,
                filetype: this.state.filetype.toString(),
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
                if (!data.error) {
                    this.setState({
                        elements: data,
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
        let selectedElements = this.getSelectedElements()
        let handler = this.handler
        let setFiletype = this.setFiletype
        let setBeginDate = this.setBeginDate
        let setEndDate = this.setEndDate
        let validateFilters = this.validateFilters
        let filterData = {
            'filetype': this.state.filetype,
            'beginDate': this.state.beginDate,
            'endDate': this.state.endDate
        }
        let beginDate = this.state.beginDate
        let endDate = this.state.endDate
        //let loading = this.state.loading

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
                        <table className="table">
                            <thead>
                            <tr>
                                <th scope="col"></th>
                                <th scope="col">Nom du fichier</th>
                                <th scope="col">Taille (en bytes)</th>
                                <th scope="col">Date de début</th>
                                <th scope="col">Date de fin</th>
                            </tr>
                            </thead>
                            <tbody>

                            {elts === [] || Object.keys(elts).length === 0 ?
                                <tr>
                                    <td colSpan='7' className="text-center">Pas de données</td>
                                </tr> :
                                Object.keys(elts).map(function (key, index) {
                                    return <RowItem key={index} item={elts[key]}
                                                    handler={handler}
                                                    selectedElements={selectedElements}
                                                    beginDate={beginDate}
                                                    endDate={endDate}
                                    />
                                })}
                            </tbody>
                        </table>
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