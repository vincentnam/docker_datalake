import React from "react";
import {NavLink, useHistory} from 'react-router-dom';
import api from '../api/api';
import {config} from "../configmeta/projects";
import {connect} from "react-redux";
import {editNameContainer} from "../store/nameContainerAction";
import {editAuthProjects, editAuthRoles, editAuthToken, editAuthLoginAdmin} from "../store/authAction";

class Header extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            anomalies: [],
            container: this.props.nameContainer.nameContainer,
        };
        this.logout = this.logout.bind(this);
        this.loadRolesProjectsUser = this.loadRolesProjectsUser.bind(this);
    }

    componentDidMount() {
        this.countData(this.state.container);
        this.loadRolesProjectsUser();
    }

    loadRolesProjectsUser() {
        api.post('auth-token', {
            token: localStorage.getItem('token')
        })
            .then((response) => {
                this.props.editAuthRoles(response.data.roles);
                this.props.editAuthProjects(response.data.projects);
                response.data.roles.forEach((role) => {
                    if(role.name === "admin"){
                        this.props.editAuthLoginAdmin(true);
                    }
                })
            })
            .catch(function (error) {
                console.log(error);
            });
    }

    logout() {
        this.props.editAuthRoles([]);
        this.props.editAuthProjects([]);
        this.props.editAuthToken("");
        this.props.editAuthLoginAdmin(false);
        localStorage.removeItem('token');
        localStorage.removeItem('isLogin');
        this.props.history.push('/');
        window.location.reload();
    }

    countData(container_name) {
        api.post('getDataAnomalyAll', {
            container_name: container_name,
            token: localStorage.getItem('token')
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
                                this.countData(event.target.value);
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
                         to="/home">
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
                        {this.props.auth.isLoginAdmin === true &&
                            <li>
                                <NavLink activeClassName="active"
                                         className="nav-item nav-link"
                                         to="/config-users">
                                    <span>Users</span>
                                </NavLink>
                            </li>
                        }
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

                <div className="d-flex justify-content-center align-content-center mt-1">
                    <div>
                        <button type="submit" className="btn btn-oran-header" onClick={this.logout}><b>Déconnexion</b>
                        </button>
                    </div>
                </div>

            </nav>
        );
        return (
            <nav className="navbar navbar-expand-lg navbar-dark">
                <div className="container">
                    <div className="form-group required col-2">
                        <SelectProjects/>
                    </div>
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
        auth: state.auth
    }
}

function WithNavigate(props) {
    let history = useHistory();
    return <Header {...props} history={history}/>
}

export default connect(mapStateToProps, {
    editNameContainer,
    editAuthRoles,
    editAuthToken,
    editAuthProjects,
    editAuthLoginAdmin
})(WithNavigate)