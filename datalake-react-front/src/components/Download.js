import React from "react";
import { Header } from './Header';

export class Download extends React.Component {
    render() {
        return(
            <div>
                <Header />
                <div class="p-4">
                    <p>Download page</p>
                    <table class="table">
                        <thead>
                            <tr>
                            <th scope="col">Id</th>
                            <th scope="col">Titre</th>
                            <th scope="col">Métadonnées</th>
                            <th scope="col"></th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <th scope="row">1</th>
                                <td>titre1</td>
                                <td>data1</td>
                                <td>
                                    <div class="form-check">
                                        <input class="form-check-input" type="checkbox" value="" id="flexCheckDefault" />
                                    </div>
                                </td>
                            </tr>
                            <tr>
                                <th scope="row">2</th>
                                <td>titre2</td>
                                <td>data2</td>
                                <td>
                                    <div class="form-check">
                                        <input class="form-check-input" type="checkbox" value="" id="flexCheckDefault" />
                                    </div>
                                </td>
                            </tr>
                            <tr>
                                <th scope="row">3</th>
                                <td>titre3</td>
                                <td>data3</td>
                                <td>
                                    <div class="form-check">
                                        <input class="form-check-input" type="checkbox" value="" id="flexCheckDefault" />
                                    </div>
                                </td>
                            </tr>
                        </tbody>
                    </table>

                    <div class="col-12">
                        <button class="btn btn-primary" type="submit">Valider</button>
                    </div>
                </div>
                
            </div>
        );
    }
}