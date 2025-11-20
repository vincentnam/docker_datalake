import React from 'react';
import { Navigate } from "react-router-dom";
import {getAuthData} from "../../utils/authUtils";

const PrivateRoute = ({ children, requiredRoles = [] }) => {
  const authData = getAuthData();

  if (!authData || authData.status !== "authenticated" || !authData.access_token) {
    return <Navigate to="/" replace />;
  }

  return children;
};

export default PrivateRoute;