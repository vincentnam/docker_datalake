import React from "react";
import { Header } from './Header';
import { ModelAddForm } from './model/ModelAddForm';
import { ModelEditForm } from './model/ModelEditForm';
import api from '../api/api';

export class Models extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            models: [],
            model: {},
            newModel: {},
            show: "",
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
        
        const Formulaire = () => {
            if (this.state.show === "") {
                return (
                    <div></div>
                );
            } else if(this.state.show === "add") {
                return (
                    <ModelAddForm/>
                );
            } else if(this.state.show === "edit") {
                return (
                    <ModelEditForm/>
                );
            }
        };


        const ListModels = () => {
            const Allmodels = this.state.models.map((model) => (
                <a>{model.label}</a>
            ));

            return (
                <div className="col-sm-4">
                    {Allmodels}
                </div>
            );
        };

        return (
            <div>
                <Header />
                <div className="container mt-4">
                    <h3>Modèle configurations</h3>
                    <Formulaire/>
                </div>
            </div>
        );
    }
}