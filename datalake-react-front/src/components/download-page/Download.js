import React from "react";
import { Header } from '../Header';
import { RowItem } from './RowItem';
import axios from 'axios';
import ReactPaginate from 'react-paginate';
import $ from 'jquery';

export class Download extends React.Component {
    selectedElements = []
    elements = {}
    url = "http://127.0.0.1:5000/raw-data"
    perPage = 3

    constructor(props) {
        super(props);
        
        // Bind the this context to the handler function
        this.handler = this.handler.bind(this);
        this.validate = this.validate.bind(this)

        // Set some state
        this.state = {
            selectedElement: {},
            elements: {},
            offset: 0
        };

        /*this.elements = { 
            0: { id: 2, title: 4, metadata: 7 }, 
            1: { id: 0, title: 10, metadata: 0}, 
            2: { id: 0, title: 0, metadata: 0 }, 
            3: { id: 0, title: 0, metadata: 0 }, 
            4: { id: 0, title: 0, metadata: 0 }, 
            5: { id: 0, title: 0, metadata: 0 } 
        }*/


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
          url: this.url,
          data: { limit: this.perPage, offset: this.state.offset },
          dataType: 'json',
          type: 'GET',
    
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

    render() {
        let elts = []
        console.log(this.state.elements)
        if(this.state.elements){
            elts = this.state.elements
            console.log(elts)
        }
        let selectedElements = this.state.selectedElements
        let handler = this.handler

        return(
            <div>
                <Header />
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
            
                                return <RowItem key={index} item={elts[key]} handler={handler} />

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