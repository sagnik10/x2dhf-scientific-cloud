import React,{useState} from 'react';
import {useDispatch,useSelector} from 'react-redux';
import {useNavigate,Link} from 'react-router-dom';
import {registerUser} from '../store/authSlice';
import QuantumBackdrop from '../components/QuantumBackdrop';
import logo from '../assets/x2dhf-logo.png';

const validEmail=value=>/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
const validPhone=value=>/^\+\d{11,13}$/.test(value.replace(/\s|-/g,''));

const Register=()=>{
 const [formData,setFormData]=useState({username:'',email:'',phone:'',password:''});
 const [localError,setLocalError]=useState('');
 const dispatch=useDispatch();
 const navigate=useNavigate();
 const {loading,error}=useSelector(state=>state.auth);
 const handleChange=e=>setFormData({...formData,[e.target.name]:e.target.value});
 const handleSubmit=async e=>{e.preventDefault();setLocalError('');if(!validEmail(formData.email)){setLocalError('Email must contain @ and a valid domain.');return;}if(formData.phone&&!validPhone(formData.phone)){setLocalError('Phone must start with + and include country code plus local number, for example +916295862826.');return;}if(formData.password.length<8){setLocalError('Password must be at least 8 characters.');return;}const result=await dispatch(registerUser({username:formData.username,email:formData.email,password:formData.password}));if(!result.error)navigate('/login');};
 return(<div className="relative flex min-h-screen items-center justify-center overflow-hidden"><QuantumBackdrop/><div className="relative w-full max-w-md rounded-lg border border-emerald-300/20 bg-slate-950/85 p-8 shadow-2xl shadow-emerald-950/50 backdrop-blur"><div className="mb-8 flex items-center gap-4"><img src={logo} alt="X2DHF" className="h-16 w-16 rounded-xl border border-emerald-300/30"/><div><h1 className="text-3xl font-bold text-white">Create Account</h1><p className="text-sm text-emerald-100/70">Run Python X2DHF jobs securely</p></div></div><form onSubmit={handleSubmit} className="space-y-4" noValidate><label className="block text-sm text-slate-300">Username<input type="text" name="username" placeholder="researcher01" value={formData.username} onChange={handleChange} required minLength="3" title="Use at least 3 characters." className="mt-1 w-full rounded-lg border border-slate-700 px-4 py-3 outline-none focus:border-emerald-400"/></label><label className="block text-sm text-slate-300">Email<input type="email" name="email" placeholder="researcher@example.com" value={formData.email} onChange={handleChange} required title="Email must contain @ and a valid domain." className="mt-1 w-full rounded-lg border border-slate-700 px-4 py-3 outline-none focus:border-emerald-400"/></label><label className="block text-sm text-slate-300">Phone<input type="tel" name="phone" placeholder="+916295862826" value={formData.phone} onChange={handleChange} title="Start with +, then country code and local number." className="mt-1 w-full rounded-lg border border-slate-700 px-4 py-3 outline-none focus:border-emerald-400"/><span className="mt-1 block text-xs text-slate-500">Example: +916295862826.</span></label><label className="block text-sm text-slate-300">Password<input type="password" name="password" placeholder="Minimum 8 characters" value={formData.password} onChange={handleChange} required minLength="8" title="Password must be at least 8 characters." className="mt-1 w-full rounded-lg border border-slate-700 px-4 py-3 outline-none focus:border-emerald-400"/></label>{(localError||error)&&<p className="text-sm text-rose-300">{localError||(typeof error==='object'?JSON.stringify(error):error)}</p>}<button type="submit" disabled={loading} className="w-full rounded-lg bg-emerald-400 py-3 font-semibold text-slate-950 hover:bg-emerald-300 disabled:bg-slate-600">{loading?'Registering...':'Register'}</button></form><p className="mt-4 text-center text-sm text-slate-300">Already registered? <Link to="/login" className="text-emerald-300 hover:underline">Login</Link></p></div></div>);
};

export default Register;
