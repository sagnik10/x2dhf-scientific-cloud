import React,{useState} from 'react';
import {Link} from 'react-router-dom';
import {authAPI} from '../api/client';
import QuantumBackdrop from '../components/QuantumBackdrop';

const validEmail=value=>/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);

const ForgotPassword=()=>{
 const [email,setEmail]=useState('');
 const [message,setMessage]=useState('');
 const [error,setError]=useState('');
 const submit=async e=>{e.preventDefault();setError('');setMessage('');if(!validEmail(email)){setError('Email must contain @ and a valid domain.');return;}try{const response=await authAPI.forgotPassword(email);setMessage(response.data.message);}catch(err){setError(err.response?.data?.email||'Unable to process reset request.');}};
 return(<div className="relative flex min-h-screen items-center justify-center overflow-hidden"><QuantumBackdrop/><div className="relative w-full max-w-md rounded-lg border border-cyan-300/20 bg-slate-950/85 p-8 shadow-2xl shadow-cyan-950/50 backdrop-blur"><h1 className="text-3xl font-bold text-white">Reset Password</h1><p className="mt-2 text-sm text-slate-300">Enter the account email. In local runserver mode this returns reset guidance instead of sending production mail.</p><form onSubmit={submit} className="mt-6 space-y-4"><label className="block text-sm text-slate-300">Email address<input type="email" value={email} onChange={e=>setEmail(e.target.value)} onBlur={()=>!validEmail(email)&&email&&setError('Email must contain @ and a valid domain.')} required title="Use a valid email such as researcher@example.com" className="mt-1 w-full rounded-lg border border-slate-700 px-4 py-3 outline-none focus:border-cyan-400"/></label>{error&&<p className="text-sm text-rose-300">{error}</p>}{message&&<p className="rounded border border-emerald-400/30 bg-emerald-500/10 p-3 text-sm text-emerald-100">{message}</p>}<button className="w-full rounded-lg bg-cyan-400 py-3 font-semibold text-slate-950 hover:bg-cyan-300">Request Reset</button></form><Link to="/login" className="mt-4 block text-center text-sm text-cyan-300 hover:underline">Back to login</Link></div></div>);
};

export default ForgotPassword;
