import React,{useState} from 'react';
import {useDispatch,useSelector} from 'react-redux';
import {useNavigate,Link} from 'react-router-dom';
import {loginUser} from '../store/authSlice';
import QuantumBackdrop from '../components/QuantumBackdrop';

const validEmail=value=>/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
const logo='/favicon.png';
const friendlyError=error=>{
 if(!error)return '';
 if(typeof error==='string')return error;
 const value=error.non_field_errors||error.detail||error.email||error.password||error.username;
 if(Array.isArray(value))return value.join(' ');
 if(typeof value==='string')return value;
 return 'Login failed. Please check the email and password.';
};

const Login=({mode='user'})=>{
 const [email,setEmail]=useState('');
 const [password,setPassword]=useState('');
 const [localError,setLocalError]=useState('');
 const dispatch=useDispatch();
 const navigate=useNavigate();
 const {loading,error}=useSelector(state=>state.auth);
 const handleSubmit=async e=>{e.preventDefault();setLocalError('');if(!validEmail(email)){setLocalError('Email must contain @ and a valid domain.');return;}if(password.length<8){setLocalError('Password must be at least 8 characters.');return;}const result=await dispatch(loginUser({email,password}));if(result.payload?.access)navigate(mode==='admin'?'/admin-dashboard':'/dashboard',{replace:true});};
 return(<div className="relative flex min-h-screen items-center justify-center overflow-hidden"><QuantumBackdrop/><div className="relative w-full max-w-md rounded-lg border border-cyan-300/20 bg-slate-950/85 p-8 shadow-2xl shadow-cyan-950/50 backdrop-blur"><div className="mb-8 flex items-center gap-4"><img src={logo} alt="X2DHF" className="h-16 w-16 rounded-xl border border-cyan-300/30"/><div><h1 className="text-3xl font-bold text-white">{mode==='admin'?'Admin Login':'X2DHF Login'}</h1><p className="text-sm text-cyan-100/70">Hartree-Fock and DFT cloud runtime</p></div></div>{mode==='admin'&&<div className="mb-4 rounded-lg border border-amber-300/20 bg-amber-400/10 p-3 text-xs leading-5 text-amber-100">Admin access requires a staff account created on the server. No default credentials are exposed in the browser.</div>}<form onSubmit={handleSubmit} className="space-y-4"><label className="block text-sm text-slate-300">Email<input type="email" placeholder="researcher@example.com" value={email} onChange={e=>{setEmail(e.target.value);setLocalError('');}} onBlur={()=>email&&!validEmail(email)&&setLocalError('Email must contain @ and a valid domain.')} required title="Use a valid email address with @ and a domain." className="mt-1 w-full rounded-lg border border-slate-700 px-4 py-3 outline-none focus:border-cyan-400"/></label><label className="block text-sm text-slate-300">Password<input type="password" placeholder="Minimum 8 characters" value={password} onChange={e=>{setPassword(e.target.value);setLocalError('');}} required minLength="8" title="Password must be at least 8 characters." className="mt-1 w-full rounded-lg border border-slate-700 px-4 py-3 outline-none focus:border-cyan-400"/></label>{(localError||error)&&<p className="rounded border border-rose-400/30 bg-rose-400/10 px-3 py-2 text-sm text-rose-100">{localError||friendlyError(error)}</p>}<button type="submit" disabled={loading} className="w-full rounded-lg bg-cyan-500 py-3 font-semibold text-slate-950 hover:bg-cyan-300 disabled:bg-slate-600">{loading?'Logging in...':'Login'}</button></form><div className="mt-4 flex justify-between text-sm"><Link to="/forgot-password" className="text-cyan-300 hover:underline">Forgot password?</Link><Link to="/register" className="text-cyan-300 hover:underline">Register</Link></div></div></div>);
};

export default Login;
