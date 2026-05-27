import React,{useState} from 'react';
import {useDispatch,useSelector} from 'react-redux';
import {useNavigate,Link} from 'react-router-dom';
import {loginUser} from '../store/authSlice';
import QuantumBackdrop from '../components/QuantumBackdrop';
import logo from '../assets/x2dhf-logo.png';

const validEmail=value=>/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);

const Login=({mode='user'})=>{
 const [email,setEmail]=useState(mode==='admin'?'admin@x2dhf.local':'');
 const [password,setPassword]=useState(mode==='admin'?'Admin@12345':'');
 const [localError,setLocalError]=useState('');
 const dispatch=useDispatch();
 const navigate=useNavigate();
 const {loading,error}=useSelector(state=>state.auth);
 const handleSubmit=async e=>{e.preventDefault();setLocalError('');if(!validEmail(email)){setLocalError('Email must contain @ and a valid domain.');return;}if(password.length<8){setLocalError('Password must be at least 8 characters.');return;}const result=await dispatch(loginUser({email,password}));if(result.payload?.access)navigate(mode==='admin'?'/admin-dashboard':'/dashboard',{replace:true});};
 const fillAdmin=()=>{setEmail('admin@x2dhf.local');setPassword('Admin@12345');};
 return(<div className="relative flex min-h-screen items-center justify-center overflow-hidden"><QuantumBackdrop/><div className="relative w-full max-w-md rounded-lg border border-cyan-300/20 bg-slate-950/85 p-8 shadow-2xl shadow-cyan-950/50 backdrop-blur"><div className="mb-8 flex items-center gap-4"><img src={logo} alt="X2DHF" className="h-16 w-16 rounded-xl border border-cyan-300/30"/><div><h1 className="text-3xl font-bold text-white">{mode==='admin'?'Admin Login':'X2DHF Login'}</h1><p className="text-sm text-cyan-100/70">Hartree-Fock and DFT cloud runtime</p></div></div><form onSubmit={handleSubmit} className="space-y-4"><label className="block text-sm text-slate-300">Email<input type="email" placeholder="researcher@example.com" value={email} onChange={e=>setEmail(e.target.value)} onBlur={()=>email&&!validEmail(email)&&setLocalError('Email must contain @ and a valid domain.')} required title="Use a valid email address with @ and a domain." className="mt-1 w-full rounded-lg border border-slate-700 px-4 py-3 outline-none focus:border-cyan-400"/></label><label className="block text-sm text-slate-300">Password<input type="password" placeholder="Minimum 8 characters" value={password} onChange={e=>setPassword(e.target.value)} required minLength="8" title="Password must be at least 8 characters." className="mt-1 w-full rounded-lg border border-slate-700 px-4 py-3 outline-none focus:border-cyan-400"/></label>{(localError||error)&&<p className="text-sm text-rose-300">{localError||(typeof error==='object'?JSON.stringify(error):error)}</p>}<button type="submit" disabled={loading} className="w-full rounded-lg bg-cyan-500 py-3 font-semibold text-slate-950 hover:bg-cyan-300 disabled:bg-slate-600">{loading?'Logging in...':'Login'}</button></form>{mode==='admin'&&<button type="button" onClick={fillAdmin} className="mt-4 w-full rounded-lg border border-cyan-300/25 bg-cyan-400/10 py-2 text-sm font-semibold text-cyan-100 hover:bg-cyan-400/20">Use dev admin credentials</button>}<div className="mt-4 flex justify-between text-sm"><Link to="/forgot-password" className="text-cyan-300 hover:underline">Forgot password?</Link><Link to="/register" className="text-cyan-300 hover:underline">Register</Link></div></div></div>);
};

export default Login;
