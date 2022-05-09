import React from "react";
import api from '../api/api';
import {toast, ToastContainer} from "react-toastify";
import {connect} from "react-redux";
import '../login.css';
import {Button, Card, Form, FormGroup, FormLabel} from "react-bootstrap";
import {editAuthToken, editAuthRoles, editAuthProjects, editAuthLogin} from "../store/authAction";
import { useHistory } from 'react-router-dom';

class Login extends React.Component {
    constructor(props) {
        super(props);
        // Set some state
        this.state = {
            user: "",
            password: "",
        };
        this.handleChange = this.handleChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);

    }

    handleChange(event) {
        const target = event.target;
        const value = target.type === 'checkbox' ? target.checked : target.value;
        const name = target.name;

        this.setState({
            [name]: value,
        });
    }

    handleSubmit(event) {
        event.preventDefault();
        let nbErrors = 0;

        if (this.state.user.trim() === '') {
            toast.error("Veuillez renseigner votre pseudo !", {
                theme: "colored",
                position: "top-right",
                autoClose: 5000,
                hideProgressBar: false,
                closeOnClick: true,
                pauseOnHover: true,
                draggable: true,
                progress: undefined,
            });
            nbErrors += 1;
        }

        if (this.state.password.trim() === '') {
            toast.error("Veuillez renseigner votre mot de passe !", {
                theme: "colored",
                position: "top-right",
                autoClose: 5000,
                hideProgressBar: false,
                closeOnClick: true,
                pauseOnHover: true,
                draggable: true,
                progress: undefined,
            });
            nbErrors += 1;
        }
        if (nbErrors === 0) {
            api.post('login', {
                user: this.state.user,
                password: this.state.password,
            })
                .then((response) =>{
                    toast.success("Vous êtes connecté !", {
                        theme: "colored",
                        position: "top-right",
                        autoClose: 1500,
                        hideProgressBar: false,
                        closeOnClick: true,
                        pauseOnHover: false,
                        draggable: true,
                        progress: undefined,
                    });
                    this.props.editAuthRoles(response.data.roles);
                    this.props.editAuthProjects(response.data.projects);
                    this.props.editAuthToken(response.data.token);
                    this.props.editAuthLogin(true);
                    this.props.history.push('/home');

                })
                .catch(function (error) {
                    toast.error("La connexion n'a pas réussi ! : " + error, {
                        theme: "colored",
                        position: "top-right",
                        autoClose: 4000,
                        hideProgressBar: false,
                        closeOnClick: true,
                        pauseOnHover: true,
                        draggable: true,
                        progress: undefined,
                    });
                })
        }
    }

    render() {
        return (
            <div>
                <nav className="navbar navbar-expand-lg navbar-dark">
                    <div className="container">
                        <div className="d-flex align-content-center">
                            <a className="navbar-brand mt-1" href="/home"><img src="images/logo-datalake.svg" alt="neOCampus"/></a>
                            <a href="/home" className="navbar-brand-text">Datalake</a>
                        </div>
                    </div>
                </nav>
                <div className="container">
                    <div className="login-wrapper">
                        <Card
                            border="primary"
                            text={'dark'}
                            style={{ width: '20rem' }}
                        >
                            <Card.Body>
                                <div className="d-flex justify-content-center">
                                    <h1>Login</h1>
                                </div>
                                <Form onSubmit={this.handleSubmit}>
                                    <FormGroup>
                                        <FormLabel>Pseudo</FormLabel>
                                        <Form.Control
                                            type="text"
                                            name="user"
                                            onChange={this.handleChange}
                                            value={this.state.user}
                                        />
                                    </FormGroup>
                                    <FormGroup>
                                        <FormLabel>Mot de passe</FormLabel>
                                        <Form.Control
                                            type="password"
                                            name="password"
                                            onChange={this.handleChange}
                                            value={this.state.password}
                                        />
                                    </FormGroup>
                                    <div className="mt-4 d-flex justify-content-center">
                                        <Button className="btn buttonModel" type="submit">Connexion</Button>
                                    </div>
                                </Form>
                            </Card.Body>
                        </Card>
                    </div>
                    <ToastContainer/>
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
    return <Login {...props} history={history} />
}

export default connect(mapStateToProps, {editAuthRoles, editAuthToken, editAuthProjects, editAuthLogin})(WithNavigate)

