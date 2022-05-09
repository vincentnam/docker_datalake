import React from "react";
import api from '../../api/api';
import {FormGroup, FormLabel, Form, Button} from "react-bootstrap";
import moment from 'moment';
import { ToastContainer, toast } from 'react-toastify';
import {connect} from "react-redux";

class Filters extends React.Component {
    constructor(props) {
        super(props);
        this.props = props
        this.state = {
            measurements: [],
            topics: [],
            measurement: "",
            topic: "",
            dt: [],
            startDate: moment().format("YYYY-MM-DD"),
            endDate: moment().format("YYYY-MM-DD"),
        };
        this.loadMeasurements(this.state.bucket);
        this.handleChange = this.handleChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
    }
    updateData(){
        this.props.data([]);
    }
    handleChange(event) {
        const target = event.target;
        const value = target.type === 'checkbox' ? target.checked : target.value;
        const name = target.name;
        if (name === "startDate") {
            if (moment(this.state.endDate).format('X') < moment(value).format('X')) {
                this.toastError('La date de début doit être inférieure à la date de fin !');
            } else {
                this.setState({
                    [name]: value,
                });
                this.updateData();
            }
        } else if (name === "endDate") {
            if (moment(this.state.startDate).format('X') > moment(value).format('X')) {
                this.toastError('La date de fin doit être supérieure à la date de début !');
            } else {
                this.setState({
                    [name]: value,
                });
                this.updateData();
            }
        } else {
            this.setState({
                [name]: value,
            });
        }

        if (name === "measurement") {
            this.props.selectMeasurement(value);
            this.loadTopics(this.state.bucket, value);
            this.props.selectTopic("");
            this.updateData();
        }
        if (name === "topic") {
            this.props.selectTopic(value);
            this.updateData();
        }
    }
    loadMeasurements() {
        api.post('measurements', {
            bucket: this.props.nameContainer.nameContainer,
            token: localStorage.getItem('token')
        })
            .then((response) => {
                this.setState({
                    measurements: response.data.measurements,
                    topics: [],
                    measurement: ""
                });
            })
            .catch(function (error) {
                console.log(error);
            });
    }
    loadTopics(bucket, measurement) {
        api.post('topics', {
            bucket: this.props.nameContainer.nameContainer,
            token: localStorage.getItem('token'),
            measurement: measurement
        })
            .then((response) => {
                this.setState({
                    topics: response.data.topics,
                    topic: "",
                });
            })
            .catch(function (error) {
                console.log(error);
            });
    }

    toastError(message){
        toast.error(`${message}`, {
            theme: "colored",
            position: "top-right",
            autoClose: 5000,
            hideProgressBar: false,
            closeOnClick: true,
            pauseOnHover: true,
            draggable: true,
            progress: undefined,
        });
    }

    handleSubmit(event) {
        event.preventDefault();
        const start = this.state.startDate;
        const end = this.state.endDate;

        if (moment(start).format('X') === moment(end).format('X')) {
            this.toastError("Veuillez modifier l'espacement entre la date de début et la date de fin !");
        } else if (this.state.bucket === null  || this.state.bucket === "") {
            this.toastError("Veuillez selectionner un bucket !")
        } else {

            api.post('getDataAnomaly', {
                measurement: this.state.measurement,
                topic: this.state.topic,
                startDate: start,
                endDate: end,
                container_name: this.props.nameContainer.nameContainer,
                token: localStorage.getItem('token')
            })
                .then((response) => {
                    let result = [];
                    for (const value of Object.entries(response.data.anomly.objects)) {
                        result.push(value[1]);
                    }
                    let data = []
                    result.forEach((dt) => {
                        data.push({
                            _id: dt._id,
                            _topic: dt.topic,
                            _value: dt.value,
                            _unit: dt.unit,
                            _datetime : dt.datetime,
                            _startDate_detection: dt.startDate_detection,
                            _endDate_detection: dt.endDate_detection,
                            //...
                        })
                    });
                    this.props.data(data);
                })
                .catch(function (error) {
                    console.log(error);
                });
        }
    }
    render() {
        const SelectMesurements = () => {
            const listMeasurements = this.state.measurements.map((measurement) => (
                <option key={measurement} value={measurement}>{measurement}</option>
            ));
            return (
                <select value={this.state.measurement} onChange={this.handleChange} multiple={false} name="measurement" className="form-select">
                    <option key="" value="">Veuillez sélectionner un measurement</option>
                    {listMeasurements}
                </select>
            );
        }
        const SelectTopics = () => {
            const listTopics = this.state.topics.map((topic) => (
                <option key={topic} value={topic}>{topic}</option>
            ));
            return (
                <select value={this.state.topic} onChange={this.handleChange} multiple={false} name="topic" className="form-select">
                    <option key="" value="">Veuillez sélectionner un topic</option>
                    {listTopics}
                </select>
            );
        }
        return (
            <div>
                <h4 className="mb-4">Anomaly Detection</h4>
                <div className="jumbotron shadow-sm">
                    <Form onSubmit={this.handleSubmit}>
                        <div className="row align-items-center">
                            <div className="form-group col-md-3 border-right">
                                <FormGroup>
                                    <FormLabel>Measurement</FormLabel>
                                    <SelectMesurements />
                                </FormGroup>
                            </div>
                            <div className="form-group col-md-3">
                                <FormGroup>
                                    <FormLabel>Topic</FormLabel>
                                    <SelectTopics />
                                </FormGroup>
                            </div>
                            <div className="form-group col-md-2">                                
                                <FormGroup>
                                    <FormLabel>Date début</FormLabel>
                                    <Form.Control type="date" onChange={this.handleChange} value={this.state.startDate} name="startDate" required />
                                </FormGroup>
                            </div>
                            <div className="form-group col-md-2">                                
                                <FormGroup>
                                    <FormLabel>Date fin</FormLabel>
                                    <Form.Control type="date" onChange={this.handleChange} value={this.state.endDate} name="endDate" required />
                                </FormGroup>
                            </div>
                            <div className="form-group col-md-1">
                                <Button type="submit" className="btn-oran btn-search float-end">
                                    <img alt="Icon Search" src="/images/icon-search.svg"/>
                                </Button>
                            </div>
                        </div>
                    </Form>
                </div>
                <ToastContainer />
            </div>
        );
    }
}

const mapStateToProps = (state) => {
    return {
        nameContainer: state.nameContainer,
        auth: state.auth
    }
}

export default connect(mapStateToProps, null)(Filters)