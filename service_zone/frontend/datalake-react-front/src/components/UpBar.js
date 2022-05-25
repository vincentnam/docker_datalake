import React from "react";
import {NavLink, useHistory} from 'react-router-dom';
import api from '../api/api';
import {config} from "../configmeta/projects";
import {connect} from "react-redux";
import {editNameContainer} from "../store/nameContainerAction";
import {editAuthProjects, editAuthRoles, editAuthToken, editAuthLoginAdmin} from "../store/authAction";
import '../navbar.css';

class UpBar extends React.Component {

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
        if(localStorage.getItem('isLogin')){
            this.countData(this.state.container);
            this.loadRolesProjectsUser();
        }
    }

    loadRolesProjectsUser() {
        api.post('auth-token', {
            token: localStorage.getItem('token')
        })
            .then((response) => {
                this.props.editAuthRoles(response.data.roles);
                this.props.editAuthProjects(response.data.projects);
                response.data.roles.forEach((role) => {
                    if (role.name === "admin") {
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
                <div className="form-group mr">
                    <select value={this.props.nameContainer.nameContainer}
                            onChange={(event) => {
                                this.props.editNameContainer(event.target.value);
                                this.countData(event.target.value);
                            }}
                            name="project" className="form-select select-project mr">
                        {listProjects}
                    </select>
                </div>
            );
        }
        return (
            <div className="upbar d-flex justify-content-end align-items-center">
                {localStorage.getItem('isLogin') &&
                    <>
                        <SelectProjects/>
                        <div className="navbar-nav-up">
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
                        </div>

                        <div className="navbar-nav-up">
                            <div className="nav-item dropdown">
                                {/* eslint-disable-next-line jsx-a11y/anchor-is-valid */}
                                <a className="nav-link dropdown-toggle" href="#" id="navbarDropdown" role="button"
                                   data-bs-toggle="dropdown" aria-expanded="false">
                                    User
                                </a>
                                <ul className="dropdown-menu" aria-labelledby="navbarDropdown">
                                    {this.props.auth.isLoginAdmin === true &&
                                        <li>
                                            <NavLink activeClassName="active"
                                                     className="nav-item nav-link text-end"
                                                     to="/config-users">
                                                Users
                                            </NavLink>
                                        </li>
                                    }
                                    <a className="text-end" style={{textDecoration: "none"}} onClick={this.logout}>Déconnexion</a>
                                </ul>
                            </div>
                        </div>
                    </>
                }


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

function WithNavigate(props) {
    let history = useHistory();
    return <UpBar {...props} history={history}/>
}

export default connect(mapStateToProps, {
    editNameContainer,
    editAuthRoles,
    editAuthToken,
    editAuthProjects,
    editAuthLoginAdmin
})(WithNavigate)