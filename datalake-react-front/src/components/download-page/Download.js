import React from "react";
import { Header } from '../Header';
import { RowItem } from './RowItem';
import axios from 'axios';
import ReactPaginate from 'react-paginate';
import $ from 'jquery';
import { Filters } from "./Filters";
import moment from "moment";
import ProgressBar from 'react-bootstrap/ProgressBar';
//import useForceUpdate from 'use-force-update';

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

        // Set some state
        this.state = {
            selectedElements: [],
            elements: {},
            offset: 0,
            filetype: '',
            dataType: '',
            beginDate: moment().format('Y-m-d'),
            endDate: moment().format('Y-m-d')
        };
    }

    componentDidMount(){
        axios.get(this.url)
            .then(res => {
                this.setState(
                    { elements: res.data }
                );
        })
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
            selectedElement: selectedElementsTemp
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
            const options = {
                onDownloadProgress: (progressEvent) => {
                    const {loaded, total} = progressEvent;
                    let percent = Math.floor( (loaded * 100) / total )
                    console.log( `${loaded}kb of ${total}kb | ${percent}%` )
                }
            }

            axios.post(this.url + '/swift-files', body)
                .then(function (result) {
                    let url = result.data.swift_zip
                    const link = document.createElement('a');
                    link.href = url;
                    
                    link.click();
                    window.URL.revokeObjectURL(url);
                })
                .catch(function (error, status) {
                    console.error(status, error.toString()); // eslint-disable-line
                });

              // empty selected elements
            this.emptySelectedlements()
        } else {
            alert('Veuillez sélectionner une métadonnée !')
        }
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
        });
      }

    setFiletype(value) {
        let filetype = value;

        this.state.filetype = filetype;
        return this.setState({filetype: this.state.filetype})
    }

    setDatatype(value) {
        let dataType = value;

        this.state.dataType = dataType;
        return this.setState({dataType: this.state.dataType})
    }

    setBeginDate(value) {
        let beginDate = value;
        this.state.beginDate = beginDate;
        return this.setState({beginDate: this.state.beginDate})
    }

    setEndDate(value) {
        let endDate = value;
        this.state.endDate = endDate;
        return this.setState({endDate: this.state.endDate})
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

                    { elts.length ? 
                            <div class="commentBox">
                                    <ReactPaginate
                                        previousLabel={'previous'}
                                        nextLabel={'next'}
                                        breakLabel={'...'}
                                        breakClassName={'break-me'}
                                        pageCount={this.state.pageCount}
                                        marginPagesDisplayed={2}
                                        pageRangeDisplayed={5}
                                        onPageChange={this.handlePageClick}
                                        activeClassName={'active'}
                                        breakClassName={'page-item'}
                                        breakLinkClassName={'page-link'}
                                        containerClassName={'pagination row justify-content-md-center'}
                                        pageClassName={'page-item'}
                                        pageLinkClassName={'page-link'}
                                        previousClassName={'page-item'}
                                        previousLinkClassName={'page-link'}
                                        nextClassName={'page-item'}
                                        nextLinkClassName={'page-link'}
                                        forcePage={this.state.selected}
                                    />
                            </div>
                        : '' }

                    { elts.length ?
                        <div class="col-12 text-center">
                            <button class="btn btn-primary" onClick={this.validate} type="submit">Download</button>
                        </div>
                    : '' }
                </div>

                {/*<ProgressBar animated now={45} />*/}
                
            </div>
        );
    }
}