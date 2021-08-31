import React from "react";
import {Header} from '../Header';
import {RowItem} from './RowItem';
import api from '../../api/api';
import $ from 'jquery';
import {Filters} from "./Filters";
import moment from "moment";
import {Paginate} from "./Paginate";
import {LoadingSpinner} from "../utils/LoadingSpinner";

export class DownloadRaw extends React.Component {
    url = process.env.REACT_APP_SERVER_NAME
    perPage = 6
    title = 'Affichage des données brutes'

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
            loading: false
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
        let offset = Math.ceil(selected * this.perPage);

        this.setState({offset: offset}, () => {
            this.loadObjectsFromServer();
        });
    };

    loadObjectsFromServer() {
        this.handleShow()
        $.ajax({
            url: this.url + '/raw-data',
            data: JSON.stringify({
                limit: this.perPage,
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
                        pageCount: Math.ceil(data.result.length / this.perPage),
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
        let loading = this.state.loading

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
                        <div className="col text-left">Résultats trouvés <span>xx</span></div>
                        <div className="col text-end">Items par page</div>
                    </div>
                    <div className="grid mt5 shadow-sm">
                        <table className="table">
                            <thead>
                            <tr>
                                <th scope="col">Id objet Swift</th>
                                <th scope="col">Container Swift</th>
                                <th scope="col">Type de fichier</th>
                                <th scope="col">Utilisateur Swift</th>
                                <th scope="col">Nom de l'objet</th>
                                <th scope="col">Meta 1</th>
                                <th scope="col">Meta 2</th>
                                <th scope="col">Date de création</th>
                                <th scope="col"></th>
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
                        <Paginate
                            elts={elts}
                            handlePageClick={this.handlePageClick}
                            selected={this.state.selected}
                            pageCount={this.state.pageCount}
                        />
                    </div>
                </div>
                <div class="p-4">
                    {elts.length ?
                        <div class="col-12 text-center">
                            <button class="btn btn-darkblue" onClick={this.validate} type="submit">Télécharger</button>
                        </div>
                        : ''}
                </div>

                <LoadingSpinner loading={this.state.loading}/>

            </div>
        );
    }
}