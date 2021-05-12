import React from "react";
import { Header } from '../Header';
import { RowItem } from './RowItem';
import axios from 'axios';
import ReactPaginate from 'react-paginate';
import $ from 'jquery';
import { Filters } from "./Filters";
//import useForceUpdate from 'use-force-update';

export class Download extends React.Component {
    selectedElements = []
    elements = {}
    url = process.env.REACT_APP_ENDPOINT
    perPage = 3

    constructor(props) {
        super(props);
        
        // Bind the this context to the handler function
        this.handler = this.handler.bind(this);
        this.validate = this.validate.bind(this)
        this.setFiletype = this.setFiletype.bind(this);
        this.setBeginDate = this.setBeginDate.bind(this);
        this.setEndDate = this.setEndDate.bind(this);

        // Set some state
        this.state = {
            selectedElement: {},
            elements: {},
            offset: 0,
            filetype: '',
            beginDate: '',
            endDate: ''
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
            //this.props.selectedElements.push(selectedElement)
            this.selectedElements.push(selectedElement)

        } else {
            //this.props.selectedElements.splice(selectedElement)
            this.selectedElements = this.selectedElements.filter( (element) => JSON.stringify(element) !== JSON.stringify(selectedElement) )
        }
    }

    validate() {
        console.log('validation data');
        let selectedElements = this.getSelectedElements()
        console.log(selectedElements)

        /*$.ajax({
            url: this.url + '/raw-file',
            type: 'GET',
      
            success: (data) => {
                let content = data
                var blob = new Blob([data], {type: "octet/stream"});
                console.log('blob')
                console.log(blob)
                const url = window.URL.createObjectURL(blob);
                const link = document.createElement('a');
                link.href = url;

                // TODO : get dynamically
                link.download = 'sensors.csv'
                
                link.click();
                window.URL.revokeObjectURL(url);
            },
      
            error: (xhr, status, err) => {
              console.error(this.url, status, err.toString()); // eslint-disable-line
            },
          });*/
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
        //const forceUpdate = useForceUpdate();

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
            this.setState({
              elements: data.result.objects,
              pageCount: Math.ceil(data.result.length / this.perPage),
            });
          },
    
          error: (xhr, status, err) => {
            console.error(this.url, status, err.toString()); // eslint-disable-line
          },
        });

        //forceUpdate()
      }

    setFiletype(value) {
        let filetype = value;

        this.state.filetype = filetype;
        this.loadObjectsFromServer()
        return this.setState({filetype: this.state.filetype})
    }

    setBeginDate(value) {
        let beginDate = value;
        this.state.beginDate = beginDate;
        this.loadObjectsFromServer()
        return this.setState({beginDate: this.state.beginDate})
    }

    setEndDate(value) {
        let endDate = value;
        this.state.endDate = endDate;
        this.loadObjectsFromServer()
        return this.setState({endDate: this.state.endDate})
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
                    data={filterData}
                />
                <div class="p-4">
                    <p>Download page</p>
                    <table class="table">
                        <thead>
                            <tr>
                                <th scope="col">Id objet Swift</th>
                                <th scope="col">Utilisateur Swift</th>
                                <th scope="col">Nom de l'objet</th>
                                <th scope="col">Date de création</th>
                                <th scope="col"></th>
                            </tr>
                        </thead>
                        <tbody>
                                
                            { Object.keys(elts).map(function(key, index){ 
            
                                return <RowItem key={index} item={elts[key]} handler={handler} selectedElements={selectedElements} />

                            }) }

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
                               
                        </tbody>
                    </table>

                    <div class="col-12">
                        <button class="btn btn-primary" onClick={this.validate} type="submit">Valider</button>
                    </div>
                </div>
                
            </div>
        );
    }
}