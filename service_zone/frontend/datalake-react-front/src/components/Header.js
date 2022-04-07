import React from "react";
import {NavLink} from 'react-router-dom';
import api from '../api/api';
import {config} from "../configmeta/projects";
import {connect} from "react-redux";
import {editNameContainer} from "../store/nameContainerAction";

class Header extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            anomalies: [],
            container: this.props.nameContainer.nameContainer
        };
    }

    componentDidMount() {
        this.countData(this.state.container);
    }

    countData(container_name) {
        api.post('getDataAnomalyAll', {
            container_name: container_name
        })
            .then((response) => {
                this.setState({
                    anomalies: response.data.anomaly
                })
            })
            .catch(function (error) {
                console.log(error);
            });
    }

    render() {
        const SelectProjects = () => {
            let projects = [config.projects];
            const listProjects = projects.map((project) => (
                project.map((p, key) =>
                    <option key={key} value={p.name_container}>{p.label}</option>
                )
            ));

            return (
                <>
                    <select value={this.props.nameContainer.nameContainer}
                            onChange={(event) => {
                                this.props.editNameContainer(event.target.value);
                                this.countData(event.target.value)
                            }}
                            name="project" className="form-select">
                        {listProjects}
                    </select>
                </>
            );
        }

        const Navbar = () => (
            <nav className="navbar-nav">
                <NavLink exact
                         activeClassName="active"
                         className="nav-item nav-link"
                         to="/">
                    Home
                </NavLink>
                <NavLink activeClassName="active"
                         className="nav-item nav-link"
                         to="/upload">
                    Upload
                </NavLink>
                <NavLink activeClassName="active"
                         className="nav-item nav-link"
                         to="/traceability">
                    Traçabilité
                </NavLink>
                <NavLink activeClassName="active"
                         className="nav-item nav-link"
                         to="/download">
                    Download
                </NavLink>
                <NavLink activeClassName="active"
                         className="nav-item nav-link"
                         to="/data-processed-visualization">
                    Data Visualization
                </NavLink>
                <div className="nav-item dropdown">
                    {/* eslint-disable-next-line jsx-a11y/anchor-is-valid */}
                    <a className="nav-link dropdown-toggle" href="#" id="navbarDropdown" role="button"
                       data-bs-toggle="dropdown" aria-expanded="false">
                        Gestion
                    </a>
                    <ul className="dropdown-menu" aria-labelledby="navbarDropdown">
                        <li>
                            <NavLink activeClassName="active"
                                     className="nav-item nav-link"
                                     to="/models">
                                <span>Models</span>
                            </NavLink>
                        </li>
                        <li>
                            <NavLink activeClassName="active"
                                     className="nav-item nav-link"
                                     to="/mqtt-config">
                                <span>Flux MQTT</span>
                            </NavLink>
                        </li>
                    </ul>
                </div>

                <NavLink activeClassName="active"
                         className="nav-item nav-link"
                         to="/detection-anomalies">
                    Anomalies
                    {this.state.anomalies.length > 0 &&
                        <span
                            className="position-absolute translate-small top-0 badge badge-secondary rounded-pill bg-danger"
                            style={{marginTop: '5px'}}>
                            {this.state.anomalies.length}
                        </span>
                    }
                </NavLink>
            </nav>
        );
        return (
            <nav className="navbar navbar-expand-lg navbar-dark">
                <div className="container">
                    <div className="form-group required col-2">
                        <SelectProjects/>
                    </div>
                    <a className="navbar-brand" href="/"><img src="images/logo-datalake.svg" alt="neOCampus"/></a>
                    <a href="/" className="navbar-brand-text">Datalake</a>
                    <button className="navbar-toggler" type="button" data-bs-toggle="collapse"
                            data-bs-target="#navbarNavAltMarkup" aria-controls="navbarNavAltMarkup"
                            aria-expanded="false"
                            aria-label="Toggle navigation">
                        <span className="navbar-toggler-icon"/>
                    </button>
                    <div className="collapse navbar-collapse" id="navbarNavAltMarkup">
                        <Navbar/>
                    </div>
                </div>
            </nav>
        );
    }
}

const mapStateToProps = (state) => {
    return {
        nameContainer: state.nameContainer,
    }
}

export default connect(mapStateToProps, {editNameContainer})(Header)