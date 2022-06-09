import React from "react";
import {connect} from "react-redux";
import {
    editAuthToken,
    editAuthRoles,
    editAuthProjects,
    editAuthLoginAdmin,
} from "../store/authAction";
import {useHistory} from 'react-router-dom';
import {editListProjectAccess, editNameContainer} from "../store/nameContainerAction";

class Info extends React.Component {
    constructor(props) {
        super(props);
        this.state = {};
    }
    render() {
        return (
            <div className="d-flex justify-content-center align-content-center">
                <div className="w-50" >
                    <p className="text-break"><b style={{color: "red"}}>Vous n'avez accès à aucun projet. Veuillez contacter votre administrateur !</b></p>
                </div>
            </div>
        )
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
    return <Info {...props} history={history}/>
}

export default connect(mapStateToProps, {
    editAuthRoles,
    editAuthToken,
    editAuthProjects,
    editAuthLoginAdmin,
    editNameContainer,
    editListProjectAccess,
})(WithNavigate)

