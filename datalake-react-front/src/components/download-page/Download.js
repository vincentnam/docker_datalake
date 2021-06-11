import React from "react";
import { Header } from '../Header';
import { RowItem } from './RowItem';
import axios from 'axios';
import api from '../../api/api';
import $ from 'jquery';
import { Filters } from "./Filters";
import moment from "moment";
import { Paginate } from "./Paginate";
import { LoadingSpinner } from "./LoadingSpinner";

export class Download extends React.Component {
    url = process.env.REACT_APP_ENDPOINT
    perPage = 6

    constructor(props) {
        super(props);
        
        // Bind the this context to the handler function
        this.handler = this.handler.bind(this);
        this.validate = this.validate.bind(this)
        this.setFiletype = this.setFiletype.bind(this);
        this.setDatatype = this.setDatatype.bind(this);
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
            dataType: '',
            beginDate: moment().format('Y-m-d'),
            endDate: moment().format('Y-m-d'),
            loading: false
        };
    }

    getSelectedElements() {
        return this.state.selectedElements;
    }

    handler(selectedElements, event) {
        let selectedElementsTemp = this.getSelectedElements()

         // if checked
         if(event.target.checked) {
            selectedElementsTemp.push(selectedElements)

        } else {
            selectedElementsTemp = selectedElementsTemp.filter( (element) => JSON.stringify(element) !== JSON.stringify(selectedElements) )
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

        if(selectedElements.length) {
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
                }).finally(function(){this.handleClose()}.bind(this))

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
    
        this.setState({ offset: offset }, () => {
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
            datatype: this.state.dataType,
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
              if(data.result) {
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

    setDatatype(value) {
        let dataType = value;
        return this.setState({dataType: dataType})
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
        if(this.state.elements){
            elts = this.state.elements
        }
        let selectedElements = this.getSelectedElements()
        let handler = this.handler
        let setFiletype = this.setFiletype
        let setBeginDate = this.setBeginDate
        let setEndDate = this.setEndDate
        let setDatatype = this.setDatatype
        let validateFilters = this.validateFilters
        let filterData = {
            'filetype': this.state.filetype,
            'beginDate': this.state.beginDate,
            'endDate': this.state.endDate
        }
        let loading = this.state.loading

        return(
            <div>
                <Header />
                <Filters 
                    setFiletype={setFiletype} 
                    setBeginDate={setBeginDate}
                    setEndDate={setEndDate}
                    setDatatype={setDatatype}
                    validateFilters={validateFilters}
                    data={filterData}
                />
                <div class="p-4">
                    <p>Download page</p>
                    <table class="table">
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

                            { !elts.length ? <tr> <td colspan='7' class="text-center">Pas de données</td> </tr> : 
                                
                             Object.keys(elts).map(function(key, index){ 
            
                                return <RowItem key={index} item={elts[key]} 
                                handler={handler} 
                                selectedElements={selectedElements} />

                            }) }
                               
                        </tbody>
                    </table>

                    <Paginate
                        elts={elts}
                        handlePageClick={this.handlePageClick}
                        selected={this.state.selected}
                        pageCount={this.state.pageCount}
                    />

                    { elts.length ?
                        <div class="col-12 text-center">
                            <button class="btn btn-primary" onClick={this.validate} type="submit">Download</button>
                        </div>
                    : '' }
                </div>

                <LoadingSpinner loading={this.state.loading} />
                
            </div>
        );
    }
}