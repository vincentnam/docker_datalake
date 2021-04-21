import React from "react";

export class Header extends React.Component {
    render() {
        return(
            <nav className="navbar navbar-default">
                <div className="container">
                    <div className="navbar-header">
                        <ul>
                            <li>
                                <a href="#">Home</a>
                            </li>
                            <li>
                                <a href="#">Data Visualization</a>
                            </li>
                            <li>
                                <a href="#">Download</a>
                            </li>
                            <li>
                                <a href="#">Upload</a>
                            </li>
                        </ul>
                    </div>
                </div>
            </nav>
        );
    }
}