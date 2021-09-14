import React from "react";
import api from '../../api/api';

export class ModelEditForm extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            models: [],
            model: {},
            newModel: {},
        };
    }
    loadModel() {
        api.get('models')
            .then((response) => {
                this.setState({
                    models: response.data.models
                });
            })
            .catch(function (error) {
                console.log(error);
            });
    }

    submitModels(){
        api.put('models/edit')
            .then((response) => {
                console.log(response)
            })
            .catch(function (error) {
                console.log(error);
            });
    }
    handleChange(event) {
        const target = event.target;
        const value = target.type === 'checkbox' ? target.checked : target.value;
        const name = target.name;

        this.setState({
            [name]: value,
        });
    }
    //handleCallbackData = (childData) =>{
    //    this.setState({dataFilters: childData})
    //}
    
    render() {
        return (
            <div>
                <h3>Model edit</h3>
            </div>
        );
    }
}