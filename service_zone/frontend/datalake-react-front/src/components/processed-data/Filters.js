import React from "react";
import api from '../../api/api';
import {FormGroup, FormLabel, Form, Button} from "react-bootstrap";
import moment from 'moment';


export class Filters extends React.Component {
    constructor(props) {
        super(props);
        this.props = props
        this.state = {
            measurements: [],
            topics: [],
            buckets: [],
            measurement: "",
            topic: "",
            bucket: "",
            dt: [],
            startDate: moment().format("YYYY-MM-DD"),
            endDate: moment().format("YYYY-MM-DD"),
        };
        this.loadBuckets();
        this.handleChange = this.handleChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
    }
    handleChange(event) {
        const target = event.target;
        const value = target.type === 'checkbox' ? target.checked : target.value;
        const name = target.name;
        if (name === "startDate") {
            if (moment(this.state.endDate).format('X') < moment(value).format('X')) {
                alert('La date de début doit être inférieure à la date de fin !');
            } else {
                this.setState({
                    [name]: value,
                });
            }
        } else if (name === "endDate") {
            if (moment(this.state.startDate).format('X') > moment(value).format('X')) {
                alert('La date de fin doit être supérieure à la date de début !');
            } else {
                this.setState({
                    [name]: value,
                });
            }
        } else {
            this.setState({
                [name]: value,
            });
        }

        if (name === "bucket") {
            this.props.selectBucket(value);
            this.loadMeasurements(value);
            this.props.selectMeasurement("");
            this.props.selectTopic("");
        }
        if (name === "measurement") {
            this.props.selectMeasurement(value);
            this.loadTopics(this.state.bucket, value);

            this.props.selectTopic("");
        }
        if (name === "topic") {
            this.props.selectTopic(value);
        }
    }
    loadBuckets() {
        api.get('bucket')
            .then((response) => {
                this.setState({
                    buckets: response.data.buckets
                });
            })
            .catch(function (error) {
                console.log(error);
            });
    }
    loadMeasurements(bucket) {
        api.post('measurements', {
            bucket: bucket
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
            bucket: bucket,
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

    handleSubmit(event) {
        event.preventDefault();
        const start = this.state.startDate;
        const end = this.state.endDate;

        if (moment(start).format('X') === moment(end).format('X')) {
            alert("Veuillez modifier l'espacement entre la date de début et la date de fin !");
        } else if (this.state.bucket === null) {
            alert("Veuillez selectionner un bucket !")
        } else if (this.state.measurement === null) {
            alert("Veuillez selectionner un measurement !")
        } else if (this.state.topic === null || this.state.topic === "") {
            alert("Veuillez selectionner un topic !")
        } else {
            api.post('dataTimeSeries', {
                bucket: this.state.bucket,
                measurement: this.state.measurement,
                topic: this.state.topic,
                startDate: moment(start).format('X'),
                endDate: moment(end).format('X'),
            })
                .then((response) => {
                    let result = [];
                    for (const [key, value] of Object.entries(response.data.dataTimeSeries[0])) {
                        result.push(value);
                    }
                    let data = []
                    result.map((dt) => {
                        data.push({
                            _time: moment.unix(dt._time / 1000).format("DD/MM/YYYY HH:mm:ss"),
                            _value: dt._value,
                            _measurement: dt._measurement,
                            topic: dt.topic,
                        })
                    });
                    this.props.data(data);
                    this.props.dataGraph(response.data.dataTimeSeriesGraph[0]);

                })
                .catch(function (error) {
                    console.log(error);
                });
        }
    }
    render() {
        const SelectBucket = () => {
            const listBuckets = this.state.buckets.map((bucket) => (
                <option key={bucket} value={bucket}>{bucket}</option>
            ));
            return (
                <select value={this.state.bucket} onChange={this.handleChange} multiple={false} name="bucket" className="form-select">
                    <option key="" value="">Veuillez sélectionner un bucket</option>
                    {listBuckets}
                </select>
            );
        }

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
                <h4 class="mb-4">Data visualization</h4>
                <div className="jumbotron shadow-sm">
                    <Form onSubmit={this.handleSubmit}>
                        <div className="row align-items-center">
                            <div className="form-group col-md-2 border-right">
                                <FormGroup>
                                    <FormLabel>Bucket</FormLabel>
                                    <SelectBucket />
                                </FormGroup>
                            </div>
                            <div className="form-group col-md-2">
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
                                    <img src="/images/icon-search.svg"/>
                                </Button>
                            </div>
                        </div>
                    </Form>
                </div>
            </div>
        );
    }
}