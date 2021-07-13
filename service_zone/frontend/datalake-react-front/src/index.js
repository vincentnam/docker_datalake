import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import reportWebVitals from './reportWebVitals';
import 'bootstrap/dist/css/bootstrap.css';
import { Home } from './components/Home';
import { DataViz } from './components/DataViz';
import { Upload } from './components/Upload';
import {
  BrowserRouter as Router,
  Switch,
  Route
} from 'react-router-dom';
import { Download } from './components/download-raw-data/Download';
import { DownloadHandleData } from './components/download-handled-data/DownloadHandleData';

ReactDOM.render(
  <React.StrictMode>
    <Router>
      <div>
        <Switch>
          <Route path="/data-visualization">
            <DataViz />
          </Route>
          <Route path="/download">
            <Download />
          </Route>
          <Route path="/upload">
            <Upload />
          </Route>
          <Route path="/download-handled-data">
            <DownloadHandleData />
          </Route>
          <Route path="/">
            <Home />
          </Route>
        </Switch>
      </div>
    </Router>
  </React.StrictMode>,
  document.getElementById('root')
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
