import React from "react";
import { ToastContainer } from 'react-toastify';
import {ProcessedDataSensors} from './data-sensors/Processd-data-sensors';
import {ProcessedDataSGE} from './data-SGE/Processd-data-SGE';
import {connect} from "react-redux";


class ProcessedDataVisualisationAll extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            container_name: this.props.nameContainer.nameContainer,
        };
    }
    render() {

        const TabDataSGE = () => {
            let tabSGE = "";
            if(this.state.container_name === "neOCampus"){
                tabSGE = (
                    <button className="nav-link" id="nav-sge-tab" data-bs-toggle="pill"
                            data-bs-target="#nav-sge" type="button" role="tab" aria-controls="nav-sge"
                            aria-selected="false">Données SGE
                    </button>
                );
            } else {
                tabSGE = <></>
            }
            return tabSGE;
        }

        const SectionDataSGE = () => {
            let sectionSGE = "";
            if(this.state.container_name === "neOCampus"){
                sectionSGE = (
                    <div className="tab-pane fade" id="nav-sge" role="tabpanel"
                         aria-labelledby="nav-sge-tab">
                        <ProcessedDataSGE/>
                    </div>
                );
            } else {
                sectionSGE = <></>
            }
            return sectionSGE;
        }

        return (
            <div>
                <div className="container main-download">
                    <nav className="tab-download">
                        <div className="nav nav-pills " id="pills-tab" role="tablist">
                            <button className="nav-link active" id="nav-sensors-tab" data-bs-toggle="pill"
                                    data-bs-target="#nav-sensors" type="button" role="tab" aria-controls="nav-sensors"
                                    aria-selected="true">Données capteurs
                            </button>
                            <TabDataSGE/>
                        </div>
                    </nav>
                    <div className="tab-content" id="pills-tabContent">
                        <div className="tab-pane fade show active" id="nav-sensors" role="tabpanel"
                            aria-labelledby="nav-sensors-tab">
                            <ProcessedDataSensors/>
                        </div>
                        <SectionDataSGE/>
                    </div>
                    <ToastContainer />
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

export default connect(mapStateToProps, null)(ProcessedDataVisualisationAll)