import React, { useState, useEffect } from "react";
import { Router, Route, Switch } from "react-router";
import ListBuckets from "./components/ListBuckets";
import BrowseBucket from "./components/BrowseBucket";
import AppLayout from "./Layout/AppLayout";
import history from "./history";
import "./App.css";
import Login from "./components/Login";
import { getBuckets } from './utils/s3client';  // Ajoutez cet import

const App = () => {


    localStorage.setItem("jwtToken","TESTTOKEN12354667")

  return (
      <Router history={history}>
        <AppLayout>
          <Switch>
            <Route exact path={[ "/"]} component={Login} />
            <Route exact path={[ "/buckets"]} component={ListBuckets} />
            <Route exact path="/buckets/:bucketName" component={BrowseBucket} />
          </Switch>
        </AppLayout>
      </Router>
    // <div>
    //   <h2>Liste des buckets</h2>
    //   <p>Statut: {status}</p>
    //   <ul>
    //     coucou
    //     {buckets_list}
    //     {var_test_func}
    //   </ul>
    // </div>
  );
};




export default App;