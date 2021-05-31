import React from "react";
import { Button, Modal, Spinner } from "react-bootstrap";

export class LoadingSpinner extends React.Component {
    constructor(props){
        super(props);
        this.props = props;
    }

    render() {
        return(
            <div>
                <Modal show={this.props.loading}>
                    <Button variant="primary" disabled>
                        <Spinner
                        as="span"
                        animation="border"
                        size="sm"
                        role="status"
                        aria-hidden="true"
                        />
                        <span className="sr-only">Loading...</span>
                    </Button>{' '}
                    <Button variant="primary" disabled>
                        <Spinner
                        as="span"
                        animation="grow"
                        size="sm"
                        role="status"
                        aria-hidden="true"
                        />
                        Loading...
                    </Button>
                </Modal>
            </div>
        );
    }
}