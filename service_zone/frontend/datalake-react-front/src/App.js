import React from 'react';
import './index.css';
import 'bootstrap/dist/css/bootstrap.css';
import 'bootstrap/dist/js/bootstrap.min.js'
import './style.css';
import 'react-toastify/dist/ReactToastify.css';
import {
    Switch,
    Route
} from 'react-router-dom';
import Login from "./components/Login";
import {connect} from "react-redux";
import Protected from "./Protected";


const App = ({auth}) => {
    return (
        <>
            <Switch>
                {localStorage.getItem('isLogin') && localStorage.getItem('token') !== "" ? (
                    <Route path='/' render={() => <Protected isAdmin={auth.isLoginAdmin} /> }/>
                ) : (
                    <Route path="/">
                        <Login/>
                    </Route>
                )}

            </Switch>
        </>
    )
}
const mapStateToProps = (state) => {
    return {
        nameContainer: state.nameContainer,
        auth: state.auth
    }
}

export default connect(mapStateToProps, null)(App)
