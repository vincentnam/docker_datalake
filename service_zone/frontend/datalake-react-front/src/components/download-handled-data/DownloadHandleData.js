import React from "react";
import { Filters } from "../download-raw-data/Filters";
import { Header } from "../Header";
import moment from "moment";
import api from '../../api/api';
import $ from 'jquery';
import { RowItem } from "./RowItem";
import { LoadingSpinner } from "../utils/LoadingSpinner";
import { Paginate } from "../download-raw-data/Paginate";

export class DownloadHandleData extends React.Component {
    url = process.env.REACT_APP_SERVER_NAME
    title = 'Affichage des données traitées'

    constructor(props) {
        super(props);

        this.handler = this.handler.bind(this);
        this.setFiletype = this.setFiletype.bind(this);
        this.setBeginDate = this.setBeginDate.bind(this);
        this.setEndDate = this.setEndDate.bind(this);
        this.validateFilters = this.validateFilters.bind(this)
        this.validate = this.validate.bind(this)

        this.state = {
            selectedElements: [],
            elements: {},
            filetype: '',
            beginDate: moment().format('Y-MM-DD'),
            endDate: moment().format('Y-MM-DD'),
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

    loadHandledDataFromServer() {
        this.handleShow()
        $.ajax({
          url: this.url + '/handled-data-list',
          data: JSON.stringify({
            beginDate: this.state.beginDate,
            endDate: this.state.endDate,
            filetype: this.state.filetype.toString()
          }),
          xhrFields: {
            withCredentials: true
         },
         crossDomain: true,
         contentType: 'application/json; charset=utf-8',
          dataType: 'json',
          type: 'POST',
    
          success: (data) => {
              if(!data.error) {
                this.setState({
                    elements: data,
                    pageCount: Math.ceil(data.length / this.perPage),
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
         if(event.target.checked) {
            selectedElementsTemp.push(selectedElements)

        } else {
            selectedElementsTemp = selectedElementsTemp.filter( (element) => JSON.stringify(element) !== JSON.stringify(selectedElements) )
        }

        this.setState({
            selectedElements: selectedElementsTemp
        })
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
            this.loadHandledDataFromServer();
        })
    }

    validate() {
        let selectedElements = this.getSelectedElements()
        let body1 = []
        let json_object = {}
        selectedElements.map(element => {
            if(element.filename == "MongoDB.json"){
                json_object.mongodb_file = true
            }

            if(element.filename == "InfluxDB.csv"){
                json_object.influxdb_file = true
            }
        })

        json_object.filetype = this.state.filetype.toString()
        json_object.beginDate = this.state.beginDate
        json_object.endDate = this.state.endDate

        body1.push(json_object)
        var body = JSON.stringify(body1)

        if(selectedElements.length) {
            this.handleShow();
            api.post('handled-data-file', body, {
                'responseType': 'arraybuffer'
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
                }).finally(function(){this.handleClose()}.bind(this))

              // empty selected elements
            this.emptySelectedlements()
        } else {
            alert('Veuillez sélectionner une métadonnée !')
        }
    }

    render() {

        let elts = []
        if(this.state.elements){
            elts = this.state.elements
        }
        let selectedElements = this.getSelectedElements()
        let handler = this.handler
        let filterData = {
            'filetype': this.state.filetype,
            'beginDate': this.state.beginDate,
            'endDate': this.state.endDate
        }
        
        return (
            <div>
                <Header />
                <Filters 
                    setFiletype={this.setFiletype} 
                    setBeginDate={this.setBeginDate}
                    setEndDate={this.setEndDate}
                    validateFilters={this.validateFilters}
                    data={filterData}
                    title={this.title}
                />

                <div class="p-4">
                    <p>Download page</p>
                    <table class="table">
                        <thead>
                            <tr>
                                <th scope="col">Nom du fichier</th>
                                <th scope="col">Taille (en bytes)</th>
                            </tr>
                        </thead>
                        <tbody>

                            { elts == [] || Object.keys(elts).length == 0 ? <tr> <td colspan='7' class="text-center">Pas de données</td> </tr> : 
                                
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

                    { Object.keys(elts).length ?
                        <div class="col-12 text-center">
                            <button class="btn btn-primary" onClick={this.validate} type="submit">Download</button>
                        </div>
                    : '' }
                </div>

                <LoadingSpinner loading={this.state.loading} />


            </div>
        )
    }
}