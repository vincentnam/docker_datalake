import React from "react";
import { Header } from '../Header';
import { RowItem } from './RowItem';
import axios from 'axios';
import ReactPaginate from 'react-paginate';
import $ from 'jquery';
import { Filters } from "./Filters";
import moment from "moment";
//import useForceUpdate from 'use-force-update';

export class Download extends React.Component {
    selectedElements = []
    elements = {}
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
            selectedElement: {},
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

    getElements() {
        return this.elements;
    }

    getSelectedElements() {
        return this.selectedElements
    }

    handler(selectedElement, event) {
         // if checked
         if(event.target.checked) {
            this.selectedElements.push(selectedElement)

        } else {
            this.selectedElements = this.selectedElements.filter( (element) => JSON.stringify(element) !== JSON.stringify(selectedElement) )
        }
    }

    validate() {
        let selectedElements = this.getSelectedElements()
        let body = []
        selectedElements.map(element => {
            console.log('swift id : ', element.swift_object_id)
            body.push({
                'object_id': element.swift_object_id,
                'container_name': element.swift_container
            })
        })

        if(selectedElements.length) {
            $.ajax({
                url: this.url + '/swift-files',
                type: 'POST',
                dataType: 'json',
                contentType: 'application/json',
                data: JSON.stringify(body),
          
                success: (data) => {
                    let url = data.swift_zip
                    const link = document.createElement('a');
                    link.href = url;
                    
                    link.click();
                    window.URL.revokeObjectURL(url);
                },
          
                error: (xhr, status, err) => {
                  console.error(this.url, status, err.toString()); // eslint-disable-line
                },
              });
        }
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
            dataType: this.state.dataType,
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
            this.setState({
              elements: data.result.objects,
              pageCount: Math.ceil(data.result.length / this.perPage),
            });
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
        this.loadObjectsFromServer();
    }

    render() {
        let elts = []
        if(this.state.elements){
            elts = this.state.elements
        }
        let selectedElements = this.state.selectedElements
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
                                <th scope="col">Date de création</th>
                                <th scope="col"></th>
                            </tr>
                        </thead>
                        <tbody>

                            { !elts.length ? <tr> <td colspan='7' class="text-center">No data found</td> </tr> : 
                                
                             Object.keys(elts).map(function(key, index){ 
            
                                return <RowItem key={index} item={elts[key]} 
                                handler={handler} 
                                selectedElements={selectedElements} />

                            }) }

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
                                        containerClassName={'pagination'}
                                        activeClassName={'active'}
                                        breakClassName={'page-item'}
                                        breakLinkClassName={'page-link'}
                                        containerClassName={'pagination'}
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
                               
                        </tbody>
                    </table>

                    { elts.length ?
                        <div class="col-12">
                            <button class="btn btn-primary" onClick={this.validate} type="submit">Valider</button>
                        </div>
                    : '' }
                </div>
                
            </div>
        );
    }
}