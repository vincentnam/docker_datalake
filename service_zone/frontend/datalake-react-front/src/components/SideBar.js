import React from "react";
import {NavLink, useHistory} from 'react-router-dom';
import {connect} from "react-redux";
import {editNameContainer} from "../store/nameContainerAction";
import {editAuthProjects, editAuthRoles, editAuthToken, editAuthLoginAdmin} from "../store/authAction";
import '../sidebar.css';

class SideBar extends React.Component {

    constructor(props) {
        super(props);
    }

    render() {
        const NavSidebar = () => (
            <nav className="navbar-nav">
                <NavLink activeClassName="active"
                         className="nav-item nav-link"
                         to="/upload">
                    <div>
                        <div className="route">Upload</div>
                    </div>
                </NavLink>
                <NavLink activeClassName="active"
                         className="nav-item nav-link "
                         to="/traceability">
                    <div className="route">Traçabilité</div>
                </NavLink>
                <NavLink activeClassName="active"
                         className="nav-item nav-link "
                         to="/download">
                    <div className="route">Download</div>
                </NavLink>
                <NavLink activeClassName="active"
                         className="nav-item nav-link "
                         to="/data-processed-visualization">
                    <div className="route">Data Visualizationw </div>
                </NavLink>
                <span className="gestion">Gestion</span>
                <NavLink activeClassName="active"
                         className="nav-item nav-link"
                         to="/models">
                    <div className="sub-route">Models</div>
                </NavLink>
                <NavLink activeClassName="active"
                         className="nav-item nav-link"
                         to="/mqtt-config">
                    <div className="sub-route">Flux MQTT</div>
                </NavLink>
                <NavLink activeClassName="active"
                         className="nav-item nav-link "
                         to="/detection-anomalies">
                    <div className="route">Anomalies</div>
                </NavLink>
            </nav>
        );
        return (
            <div className="col-2 sidebar">
                <div className="title mt-4 mb-4">
                    <NavLink activeClassName="active"
                             className="nav-item nav-link d-flex justify-content-center align-content-center"
                             to="/home">
                        <img src="images/logo-datalake.svg" alt="neOCampus"/> Datalake
                    </NavLink>
                </div>
                {localStorage.getItem('isLogin') &&
                    <NavSidebar/>
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
    return <SideBar {...props} history={history}/>
}

export default connect(mapStateToProps, {
    editNameContainer,
    editAuthRoles,
    editAuthToken,
    editAuthProjects,
    editAuthLoginAdmin
})(WithNavigate)