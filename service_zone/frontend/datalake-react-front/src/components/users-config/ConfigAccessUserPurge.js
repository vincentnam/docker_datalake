import React from "react";
import {Form, Button} from "react-bootstrap";
import {ToastContainer, toast} from 'react-toastify';
import {connect} from "react-redux";
import {purgeUsers} from "../../hook/Users-assignment-roles-projects/Users";

class ConfigAccesUserPurge extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            user: {},
            selectRole: {},
            selectProject: {}
        };
        this.submitConfig = this.submitConfig.bind(this);
        this.close = this.close.bind(this);

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

    componentDidMount() {
        this.setState({
        });
    }

    submitConfig(event) {
        event.preventDefault();
        purgeUsers(localStorage.getItem('token')).then((r) => {
            if (r.result) {
                toast.success(`La purge des utilisateurs supprimés dans LDAP est effectuée !`, {
                    theme: "colored",
                    position: "top-right",
                    autoClose: 5000,
                    hideProgressBar: false,
                    closeOnClick: true,
                    pauseOnHover: true,
                    draggable: true,
                    progress: undefined,
                });
                this.close();
            }
        });
    }

    close() {
        this.props.close();
    }

    render() {
        return (
            <div>
                <Form onSubmit={this.submitConfig}>
                    <div className="d-flex justify-content-between mt-4">
                        <Button className="btn buttonModel" type="submit">Valider</Button>
                        <Button
                            type="button"
                            className="btn buttonClose"
                            onClick={this.close}>
                            Fermer
                        </Button>
                    </div>
                </Form>
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

export default connect(mapStateToProps, null)(ConfigAccesUserPurge)