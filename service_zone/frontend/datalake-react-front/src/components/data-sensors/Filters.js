import React from "react";
import {FormGroup, FormLabel, Form, Button} from "react-bootstrap";
import moment from 'moment';
import {ToastContainer, toast} from 'react-toastify';
import {connect} from "react-redux";
import {loadInfoUser} from "../../hook/User/User";
import {dataSensors, measurementsSensors, topicsSensors} from "../../hook/Data-visualisation/Data-visualisation";

class Filters extends React.Component {
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
            container_name: this.props.nameContainer.nameContainer
        };
        this.handleChange = this.handleChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
        this.loadMeasurements = this.loadMeasurements.bind(this);
        this.loadRolesProjectsUser = this.loadRolesProjectsUser.bind(this);
    }

    updateData() {
        this.props.dataGraph({});
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

        if (name === "bucket") {
            this.props.selectBucket(value);
            this.loadMeasurements();
            this.props.selectMeasurement("");
            this.props.selectTopic("");
            this.updateData();
        }
        if (name === "measurement") {
            this.props.selectMeasurement(value);
            this.loadTopics(value);
            this.props.selectTopic("");
            this.updateData();
        }
        if (name === "topic") {
            this.props.selectTopic(value);
            this.updateData();
        }
    }

    componentDidMount() {
        if (this.props.nameContainer.nameContainer !== "") {
            this.setState({
                container_name: this.props.nameContainer.nameContainer,
            })
            this.loadMeasurements();
        } else {
            this.loadRolesProjectsUser();
        }

    }

    loadRolesProjectsUser() {
        const info = loadInfoUser(localStorage.getItem('token'));
        info.then((response) => {
            this.setState({container_name: response.container_name});
            if (response.container_name !== "") {
                this.loadMeasurements();
            }
        });
    }


    loadMeasurements() {
        if (this.state.container_name !== "") {
            const measurements = measurementsSensors(this.state.container_name, localStorage.getItem('token'))
            measurements.then((response) => {
                this.setState({
                    measurements: response.measurements,
                    topics: [],
                    measurement: "",
                    topic: ""
                });
            });
        }
    }

    loadTopics(measurement) {
        const topics = topicsSensors(this.props.nameContainer.nameContainer, localStorage.getItem('token'), measurement)
        topics.then((response) => {
            this.setState({topics: response.topics, topic: ""});
        });
    }

    toastError(message) {
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
        } else if (this.state.measurement === null || this.state.measurement === "") {
            this.toastError("Veuillez selectionner un measurement !")
        } else if (this.state.topic === null || this.state.topic === "") {
            this.toastError("Veuillez selectionner un topic !")
        } else {
            const data = dataSensors(this.props.nameContainer.nameContainer, this.state.measurement, this.state.topic, start, end, localStorage.getItem('token'))
            data.then((response) => {
                this.props.data(response.data);
                this.props.dataGraph(response.dataGraph);
            });
        }
    }

    render() {
        const SelectBucket = () => {
            const listBuckets = this.state.buckets.map((bucket) => (
                <option key={bucket} value={bucket}>{bucket}</option>
            ));
            return (
                <select value={this.state.bucket} onChange={this.handleChange} multiple={false} name="bucket"
                        className="form-select">
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
                <select value={this.state.measurement} onChange={this.handleChange} multiple={false} name="measurement"
                        className="form-select">
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
                <select value={this.state.topic} onChange={this.handleChange} multiple={false} name="topic"
                        className="form-select">
                    <option key="" value="">Veuillez sélectionner un topic</option>
                    {listTopics}
                </select>
            );
        }
        return (
            <div>
                <div className="jumbotron shadow">
                    <Form onSubmit={this.handleSubmit}>
                        <div className="row align-items-center">
                            <div className="form-group col-md-2 border-right" hidden>
                                <FormGroup>
                                    <FormLabel>Bucket</FormLabel>
                                    <SelectBucket/>
                                </FormGroup>
                            </div>
                            <div className="form-group col-md-2">
                                <FormGroup>
                                    <FormLabel>Measurement</FormLabel>
                                    <SelectMesurements/>
                                </FormGroup>
                            </div>
                            <div className="form-group col-md-3">
                                <FormGroup>
                                    <FormLabel>Topic</FormLabel>
                                    <SelectTopics/>
                                </FormGroup>
                            </div>
                            <div className="form-group col-md-2">
                                <FormGroup>
                                    <FormLabel>Date début</FormLabel>
                                    <Form.Control type="date" onChange={this.handleChange} value={this.state.startDate}
                                                  name="startDate" required/>
                                </FormGroup>
                            </div>
                            <div className="form-group col-md-2">
                                <FormGroup>
                                    <FormLabel>Date fin</FormLabel>
                                    <Form.Control type="date" onChange={this.handleChange} value={this.state.endDate}
                                                  name="endDate" required/>
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
                <ToastContainer/>
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
