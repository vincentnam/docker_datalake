import React, { useState, useEffect } from "react";
import { Router, Route, Switch } from "react-router";
import ListBuckets from "./components/ListBuckets";
import BrowseBucket from "./components/BrowseBucket";
import AppLayout from "./Layout/AppLayout";
import history from "./history";
import "./App.css";
import { getBuckets } from './utils/s3client';  // Ajoutez cet import

const App = () => {

// const [buckets, setBuckets] = useState([]);
  // const [status, setStatus] = useState('Initializing...');
  // const [buckets_list, setBucket_list] = useState(null)
  // const [var_test_func, set_var_test_func]= useState(null);
  // const API_BASE_URL = 'http://10.5.255.2:5000';
  //       console.log(getBuckets)
  // useEffect(() => {
    localStorage.setItem("jwtToken","TESTTOKEN12354667")
  //   const fetchBuckets = async () => {
  //   try {
  //     console.log("PIPI")
  //     const token = localStorage.getItem('jwtToken');  // Récupérez JWT stocké (ex. post-login)
  //     const response = await fetch('http://10.5.255.2:5000/buckets', {
  //       method: 'GET',
  //       headers: {
  //         'Authorization': `Bearer ${token}`,
  //         'Content-Type': 'application/json',
  //       },
  //     });
  //
  //
  //     if (!response.ok) throw new Error(`HTTP ${response.status}`);
  //     const data = await response.json();
  //     console.log(data)
  //
  //     console.log(data.buckets)
  //     console.log("COUCOU")
  //
  //
  //     setBuckets(buckets => ([...buckets,...data.buckets]));
  //     console.log("COUCOU")
  //     console.log(buckets)
  //
  //     setStatus('Buckets listés');
  //
  //   } catch (err) {
  //
  //     setStatus(`Erreur: ${err.message}`);
  //     console.error('Erreur complète:', err);
  //   }
  // };
  // fetchBuckets();
  //
  //
  // }, []);
  //
  // useEffect(() => {
  //   console.log('Buckets mis à jour:', buckets);
  //   setBucket_list(buckets.map((bucket) => (
  //         <li key={bucket.name}>{bucket.name}</li>
  //       ))
  //   )
  //
  // }, [buckets]);
  // useEffect(() => {
  //   const fetchObjects = async () => {
  //     try {
  //       const data = await getBuckets();
  //       console.log("BITE")
  //       console.log(data)
  //       set_var_test_func(data);
  //     } catch (err) {
  //       console.error(err);
  //     }
  //   };
  //   fetchObjects();
  //
  // }, []);
  // useEffect(() => {
  //   console.log("TEST DES FONCTIONS")
  //   console.log(  var_test_func)
  //
  //   console.log("FI?N TEST DES FONCTIONS")
  // }, [ var_test_func]);

  // useEffect(() => {
  //   const s3 = new S3Client({
  //     region: 'us-east-1',
  //     endpoint: '10.5.10.1:8080',
  //     credentials: {
  //       accessKeyId: 'test:tester',
  //       secretAccessKey: 'testing',
  //     },
  //     forcePathStyle: true,
  //
  //   });
  //
  //   const fetchBuckets = async () => {
  //     try {
  //       const data = await s3.send(new ListBucketsCommand({}));
  //       setBuckets(data.Buckets || []);
  //       setStatus('Buckets listés');
  //     } catch (err) {
  //       setStatus(`Erreur: ${err.name} - ${err.message}`);
  //       console.error('Erreur complète:', err); // Log détaillé
  //     }
  //   };
  //
  //   fetchBuckets();
  //   console.log('Buckets', buckets);
  // }, []);

  return (
      <Router history={history}>
        <AppLayout>
          <Switch>
            <Route exact path={["/", "/buckets"]} component={ListBuckets} />
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