import React from "react";
import { Header } from './Header';

export class DataViz extends React.Component {
    render() {
        return(
            <div>
                <Header />
                <div class="p-4">
                    <p>Data Visualization</p>
                </div>
            </div>
        );
    }
}