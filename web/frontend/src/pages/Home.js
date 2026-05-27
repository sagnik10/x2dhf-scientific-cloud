import React from 'react';
import {Link} from 'react-router-dom';
import QuantumBackdrop from '../components/QuantumBackdrop';
import logo from '../assets/x2dhf-logo.png';

const features=['X2DHF-style input cards','HF, DFT, HFS, OED, TED, SCMC modes','Libxc-style functional labels','Live stdout and parsed energies','Saved user history','Admin analytics'];

const Home=()=>(
 <div className="relative min-h-screen overflow-hidden bg-slate-950 text-slate-100">
  <QuantumBackdrop/>
  <header className="relative z-10 mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-4 px-4 py-4 sm:px-6 lg:px-8">
   <div className="flex items-center gap-3"><img src={logo} alt="X2DHF" className="h-11 w-11 rounded-lg border border-cyan-300/30 shadow-lg shadow-cyan-500/10"/><div><div className="text-xl font-black text-white">X2DHF</div><div className="text-xs text-cyan-100/70">Python HF and DFT SaaS</div></div></div>
   <nav className="flex flex-wrap gap-2"><Link to="/login" className="rounded-lg border border-cyan-300/25 px-4 py-2 text-sm text-cyan-100 hover:bg-cyan-400/10">Login</Link><Link to="/admin-login" className="rounded-lg border border-emerald-300/25 px-4 py-2 text-sm text-emerald-100 hover:bg-emerald-400/10">Admin</Link><Link to="/register" className="rounded-lg bg-cyan-300 px-4 py-2 text-sm font-bold text-slate-950 hover:bg-white">Start</Link></nav>
  </header>
  <main className="relative z-10 mx-auto grid min-h-[calc(100vh-76px)] max-w-7xl grid-cols-1 items-center gap-6 px-4 pb-8 sm:px-6 lg:grid-cols-[1.05fr_.95fr] lg:px-8">
   <section className="hero-console rounded-lg border border-cyan-300/10 bg-slate-950/60 p-6 shadow-2xl shadow-cyan-950/30 backdrop-blur">
    <div className="font-mono text-xs uppercase tracking-[.35em] text-cyan-300/75">Local quantum runtime</div>
    <h1 className="mt-3 max-w-4xl text-4xl font-black leading-tight text-white sm:text-5xl lg:text-6xl">Production workspace for Python Hartree-Fock and DFT.</h1>
    <p className="mt-4 max-w-2xl text-base leading-7 text-slate-300">Build X2DHF-compatible inputs, control grids and SCF iterations, load repository samples, run Python computations locally, and keep outputs tied to user/admin analytics.</p>
    <div className="mt-6 flex flex-wrap gap-3"><Link to="/computations" className="rounded-lg bg-cyan-300 px-5 py-3 font-bold text-slate-950 shadow-lg shadow-cyan-500/20 hover:bg-white">Open Runtime</Link><Link to="/register" className="rounded-lg border border-slate-600 px-5 py-3 text-slate-100 hover:bg-slate-900">Create Account</Link></div>
   </section>
   <section className="grid grid-cols-1 gap-3 sm:grid-cols-2">
    {features.map((item,index)=><div key={item} className="glass-panel rounded-lg border border-cyan-300/10 bg-slate-950/70 p-4 shadow-xl shadow-slate-950/30"><div className="font-mono text-xs text-cyan-300/70">{String(index+1).padStart(2,'0')}</div><div className="mt-2 font-semibold text-white">{item}</div><p className="mt-2 text-xs leading-5 text-slate-400">Guided controls, clear prompts, and saved runtime output for repeatable scientific workflows.</p></div>)}
   </section>
  </main>
 </div>
);

export default Home;
