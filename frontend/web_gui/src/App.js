import React from "react";
import { Router, Route, Switch } from "react-router";
import ListBuckets from "./components/ListBuckets";
import BrowseBucket from "./components/BrowseBucket";
import AppLayout from "./Layout/AppLayout";
import history from "./history";
import "./App.css";

const App = () => {
  return (
    <Router history={history}>
      <AppLayout>
        <Switch>
          <Route exact path={["/", "/buckets"]} component={ListBuckets} />
          <Route exact path="/buckets/:bucketName" component={BrowseBucket} />
        </Switch>
      </AppLayout>
    </Router>
  );
};

export default App;