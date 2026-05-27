import React,{useEffect}from'react';
import {BrowserRouter as Router,Routes,Route,Navigate}from'react-router-dom';
import {useDispatch,useSelector}from'react-redux';
import Home from'./pages/Home';
import Login from'./pages/Login';
import Register from'./pages/Register';
import ForgotPassword from'./pages/ForgotPassword';
import Dashboard from'./pages/Dashboard';
import AdminDashboard from'./pages/AdminDashboard';
import Computations from'./pages/Computations';
import Results from'./pages/Results';
import Settings from'./pages/Settings';
import Learn from'./pages/Learn';
import Layout from'./components/Layout';
import ProtectedRoute from'./components/ProtectedRoute';
import {fetchCurrentUser,restoreAuth}from'./store/authSlice';

const App=()=>{
 const dispatch=useDispatch();
 const {isAuthenticated,token,user,hydrating}=useSelector(state=>state.auth);
 useEffect(()=>{const storedToken=localStorage.getItem('token');if(storedToken&&!token)dispatch(restoreAuth(storedToken));},[dispatch,token]);
 useEffect(()=>{if(isAuthenticated&&!user)dispatch(fetchCurrentUser());},[dispatch,isAuthenticated,user]);
 return <Router><Routes><Route path="/" element={<Home/>}/><Route path="/login" element={<Login mode="user"/>}/><Route path="/admin-login" element={<Login mode="admin"/>}/><Route path="/forgot-password" element={<ForgotPassword/>}/><Route path="/register" element={<Register/>}/><Route element={<ProtectedRoute isAuthenticated={isAuthenticated} user={user} hydrating={hydrating}><Layout/></ProtectedRoute>}><Route path="/dashboard" element={<Dashboard/>}/><Route path="/computations" element={<Computations/>}/><Route path="/results" element={<Results/>}/><Route path="/learn" element={<Learn/>}/><Route path="/settings" element={<Settings/>}/><Route path="/billing" element={<Navigate to="/dashboard" replace/>}/></Route><Route element={<ProtectedRoute isAuthenticated={isAuthenticated} user={user} hydrating={hydrating} requireAdmin><Layout/></ProtectedRoute>}><Route path="/admin-dashboard" element={<AdminDashboard/>}/></Route><Route path="*" element={<Navigate to={isAuthenticated?'/dashboard':'/'}/>}/></Routes></Router>;
};

export default App;
