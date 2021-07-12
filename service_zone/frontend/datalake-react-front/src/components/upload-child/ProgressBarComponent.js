import React from "react";
import { Button, Modal, Spinner, ProgressBar } from "react-bootstrap";

export class ProgressBarComponent extends React.Component {
    constructor(props){
        super(props);
        this.props = props;
    }

    render() {
        return(
            <div>
                <Modal show={this.props.loading}>
                    <Button variant="primary" disabled>
                        <Modal.Header>
                            {this.props.text}
                        </Modal.Header>
                        <Modal.Body>
                            <ProgressBar now={this.props.percentProgressBar} animated label={`${this.props.percentProgressBar}%`} />
                        </Modal.Body>
                    </Button>{' '}
                </Modal>
            </div>
        );
    }
}