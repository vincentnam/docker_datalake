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
            show: "add",
        };
        this.loadModel = this.loadModel.bind(this);
    }
    componentDidMount() {
        this.loadModel();
    }

    loadModel() {
        api.get('models/all')
            .then((response) => {
                this.setState({
                    models: response.data.models.data
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
    //    this.setState({model: childData})
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
                <a href="" className="mt-2" key={model._id}><b>{model.label}</b></a>
            ));

            return (
                <div className="col-sm-2 card modelsList pt-2 pb-2">
                    <h5>Liste des modèles de métadonnées</h5>
                    {Allmodels}
                </div>
            );
        };

        return (
            <div>
                <Header />
                <div className="container mt-4 mb-4">
                    <h3>Modèle configurations</h3>
                    <div className="row d-flex justify-content-between mt-4">
                        <ListModels />
                        <Formulaire/>
                    </div>
                    
                </div>
            </div>
        );
    }
}