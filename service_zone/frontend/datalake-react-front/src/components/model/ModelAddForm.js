import React from "react";

export class ModelAddForm extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            models: [],
            model: {},
            newModel: {},
        };
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
                <h3>Modèle Add</h3>
            </div>
        );
    }
}