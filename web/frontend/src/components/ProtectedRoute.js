import React from 'react';
import {Navigate}from'react-router-dom';

const ProtectedRoute=({isAuthenticated,user,hydrating,requireAdmin=false,children})=>{
 if(hydrating)return <div className="flex min-h-screen items-center justify-center bg-slate-950 text-slate-100">Loading secure workspace...</div>;
 if(!isAuthenticated)return <Navigate to="/login" replace/>;
 if(requireAdmin&&!(user?.is_staff||user?.is_superuser))return <Navigate to="/dashboard" replace/>;
 return children;
};

export default ProtectedRoute;
