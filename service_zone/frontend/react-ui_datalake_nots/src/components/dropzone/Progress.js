import React, { Component } from "react";
import "./Progress.css";
import * as d3ScaleChromatic from 'd3-scale-chromatic'


class Progress extends Component {
    constructor(props) {
        super(props);
        this.state = {};
    }

    componentDidUpdate(prevProps, prevState, snapshot) {
        console.log(this.props.progress/100)
        console.log(d3ScaleChromatic)
        console.log(d3ScaleChromatic.interpolateOranges(this.props.progress/100))
    }

    render() {
        return (
            <div className="ProgressBar">
                <div
                    className={"Progress"}
                    style={{ width: this.props.progress + "%" , backgroundColor: (d3ScaleChromatic.interpolateOranges(0.2 + this.props.progress/300))}}

                />
            </div>
        );
    }
}

export default Progress;
