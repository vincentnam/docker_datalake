import React from "react";
import { Header } from '../Header';
import { RowItem } from './RowItem';

export class Download extends React.Component {
    selectedElements = []

    constructor(props) {
        super(props);
        
        // Bind the this context to the handler function
        this.handler = this.handler.bind(this);
        this.validate = this.validate.bind(this)

        // Set some state
        this.state = {
            selectedElement: {}
        };

        this.elements = { 
            0: { id: 2, title: 4, metadata: 7 }, 
            1: { id: 0, title: 10, metadata: 0}, 
            2: { id: 0, title: 0, metadata: 0 }, 
            3: { id: 0, title: 0, metadata: 0 }, 
            4: { id: 0, title: 0, metadata: 0 }, 
            5: { id: 0, title: 0, metadata: 0 } 
        }
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
            //this.props.selectedElements.splice(selectedElement)
            this.selectedElements = this.selectedElements.filter( (element) => JSON.stringify(element) !== JSON.stringify(selectedElement) )
        }
    }

    validate() {
        console.log('validation data');
        let selectedElements = this.getSelectedElements()
        console.log(selectedElements)
    }

    render() {
        let elts = this.getElements()
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
                            <th scope="col">Id</th>
                            <th scope="col">Titre</th>
                            <th scope="col">Métadonnées</th>
                            <th scope="col"></th>
                            </tr>
                        </thead>
                        <tbody>

                        { Object.keys(elts).map(function(key, index){ 
        
                            return <RowItem key={index} item={elts[key]} handler={handler} />

                           }) }
                               
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