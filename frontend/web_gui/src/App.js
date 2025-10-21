import React, { useState, useEffect } from "react";
import { Router, Route, Switch } from "react-router";
import ListBuckets from "./components/ListBuckets";
import BrowseBucket from "./components/BrowseBucket";
import AppLayout from "./Layout/AppLayout";
import history from "./history";
import "./App.css";


const App = () => {
const [buckets, setBuckets] = useState([]);
  const [status, setStatus] = useState('Initializing...');


  useEffect(() => {
  const fetchBuckets = async () => {
    try {
      console.log("PIPI")
      const token = localStorage.getItem('jwtToken');  // Récupérez JWT stocké (ex. post-login)
      const response = await fetch('http://localhost:5000/buckets', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      console.log("PIPI")
      console.log("PIPI")
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();
      console.log(data)
      console.log(data.buckets)
      console.log("COUCOU")
      setBuckets([...data.buckets]);
      console.log("APRES COUCOU")
      console.log(data.buckets)
      console.log(buckets)
      setStatus('Buckets listés');
      console.log(buckets)
      console.log("PIPI")
    } catch (err) {

      setStatus(`Erreur: ${err.message}`);
      console.error('Erreur complète:', err);
    }
  };

  fetchBuckets();
  console.log('Buckets', buckets);
}, [buckets]);




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
    <div>
      <h2>Liste des buckets</h2>
      <p>Statut: {status}</p>
      <ul>
        {buckets.map((bucket) => (
          <li key={bucket.Name}>{bucket.Name}</li>
        ))}
      </ul>
    </div>
  );
};

      // <Router history={history}>
      //   <AppLayout>
      //     <Switch>
      //       <Route exact path={["/", "/buckets"]} component={ListBuckets} />
      //       <Route exact path="/buckets/:bucketName" component={BrowseBucket} />
      //     </Switch>
      //   </AppLayout>
      // </Router>


export default App;