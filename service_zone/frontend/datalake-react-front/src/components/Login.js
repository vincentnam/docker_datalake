import React from "react";
import {toast, ToastContainer} from "react-toastify";
import {connect} from "react-redux";
import '../login.css';
import {Button, Card, Form, FormGroup, FormLabel} from "react-bootstrap";
import {
    editAuthToken,
    editAuthRoles,
    editAuthProjects,
    editAuthLoginAdmin
} from "../store/Auth/authAction";
import {useHistory} from 'react-router-dom';
import SideBar from "./SideBar";
import UpBar from "./UpBar";
import {editListProjectAccess, editNameContainer} from "../store/Container/nameContainerAction";
import {login} from "../hook/Login/Login";

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
            login(this.state.user, this.state.password, this.props).then((r) => {
                if (r.result){
                    toast.success("Vous êtes connecté !", {
                        theme: "colored",
                        position: "top-right",
                        autoClose: 3000,
                        hideProgressBar: false,
                        closeOnClick: true,
                        pauseOnHover: false,
                        draggable: true,
                        progress: undefined,
                    });
                } else {
                    toast.error("La connexion n'a pas réussi ! : Veuillez vérifier votre pseudo et votre mot de passe sinon veuillez contacter votre administrateur ! ", {
                        theme: "colored",
                        position: "top-right",
                        autoClose: 4000,
                        hideProgressBar: false,
                        closeOnClick: true,
                        pauseOnHover: true,
                        draggable: true,
                        progress: undefined,
                    });
                }
            });
        }
    }

    render() {
        return (
            <div className="">
                <UpBar/>
                <div className="row m-0">
                    <SideBar/>
                    <div className="col-10" style={{marginLeft: "15%"}}>
                        <div className="container">
                            <div className="login-wrapper">
                                <Card
                                    border="primary"
                                    text={'dark'}
                                    style={{width: '20rem'}}
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
                        </div>
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
    return <Login {...props} history={history}/>
}

export default connect(mapStateToProps, {
    editAuthRoles,
    editAuthToken,
    editAuthProjects,
    editAuthLoginAdmin,
    editNameContainer,
    editListProjectAccess
})(WithNavigate)

