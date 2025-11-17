import React from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import ListBuckets from "./components/ListBuckets";
import BrowseBucket from "./components/BrowseBucket";
import AppLayout from "./Layout/AppLayout";
import "./App.css";
import Login from "./components/Login";
import PrivateRoute from "./components/Authentication/PrivateRoute";
const App = () => {
  console.log(localStorage.getItem("jwtToken"));
  return (
    <BrowserRouter>
      <AppLayout>
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/buckets" element={<PrivateRoute requiredRoles={['user']}><ListBuckets /></PrivateRoute>} />
          <Route path="/buckets/:bucketName" element={<PrivateRoute requiredRoles={['user']}><BrowseBucket /></PrivateRoute>} />
        </Routes>
      </AppLayout>
    </BrowserRouter>
  );
};




export default App;