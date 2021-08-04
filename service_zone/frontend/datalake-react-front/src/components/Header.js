import React from "react";
import logo from '../logo_datalake.png'

export class Header extends React.Component {
    render() {
        return (
            <div class="header">
                <div class="header_nav" />
                <div class="header_links">
                    <span class="datalake_link">
                        <a href="/">Datalake</a>
                    </span>
                    <span class="upload_link">
                        <a href="/upload">Upload</a>
                    </span>
                    <span class="homepage_link">
                        <a href="/">Home</a>
                    </span>
                    <span class="download_link">
                        <a href="/download">Download</a>
                    </span>
                    <span class="datavisualization_link">
                        <a href="/data-processed-visualization">Data Visualization</a>
                    </span>
                </div>
                <div class="datalake_logo">
                    <img src={logo}></img>
                </div>
            </div>
        );
    }
}