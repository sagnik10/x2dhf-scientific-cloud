import React from 'react';
import {Outlet,NavLink,useNavigate}from'react-router-dom';
import {useDispatch,useSelector}from'react-redux';
import {logoutUser}from'../store/authSlice';
import logo from'../assets/x2dhf-logo.png';

const baseLinks=[['/dashboard','Dashboard','01'],['/computations','Computations','02'],['/results','Results','03'],['/learn','Physics','04'],['/settings','Settings','05']];
const adminLink=['/admin-dashboard','Admin','06'];
const navClass=({isActive})=>`group flex shrink-0 items-center gap-2 rounded-lg px-3 py-2 text-sm transition lg:gap-3 lg:px-4 lg:py-3 ${isActive?'border border-slate-950 bg-slate-950 text-white shadow-sm':'text-slate-700 hover:bg-slate-100 hover:text-slate-950'}`;

const Layout=()=>{
 const dispatch=useDispatch();
 const navigate=useNavigate();
 const {user}=useSelector(state=>state.auth);
 const isAdmin=!!(user?.is_staff||user?.is_superuser);
 const links=isAdmin?[...baseLinks,adminLink]:baseLinks;
 const handleLogout=()=>{dispatch(logoutUser());navigate('/login',{replace:true});};
 return <div className="min-h-screen bg-white text-slate-950 lg:flex">
  <aside className="flex border-b border-slate-200 bg-white shadow-sm lg:sticky lg:top-0 lg:h-screen lg:w-72 lg:flex-col lg:border-b-0 lg:border-r">
   <div className="flex min-w-0 items-center gap-3 p-4 lg:block lg:p-6"><NavLink to="/dashboard" className="flex items-center gap-3"><img src={logo} alt="X2DHF" className="h-11 w-11 rounded-lg border border-slate-200 shadow-sm lg:h-12 lg:w-12"/><div><h1 className="text-xl font-black tracking-wide text-slate-950 lg:text-2xl">X2DHF</h1><p className="hidden text-xs text-slate-500 sm:block">Python HF and DFT SaaS</p></div></NavLink><div className="ml-auto hidden rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-2 text-xs text-emerald-900 lg:ml-0 lg:mt-5 lg:block lg:px-4 lg:py-3"><div className="font-mono uppercase tracking-[.24em] text-emerald-700">Runtime</div><div className="mt-1 font-semibold">Python kernel online</div></div></div>
   <nav className="flex flex-1 gap-2 overflow-x-auto px-3 pb-3 lg:block lg:space-y-2 lg:overflow-y-auto lg:overflow-x-hidden lg:px-4 lg:pb-4">{links.map(([to,label,index])=><NavLink key={to} to={to} className={navClass}><span className="font-mono text-xs text-blue-700">{index}</span><span>{label}</span><span className="ml-auto hidden h-1.5 w-1.5 rounded-full bg-transparent transition group-hover:bg-slate-950 lg:block"/></NavLink>)}<button onClick={handleLogout} className="shrink-0 rounded-lg px-3 py-2 text-left text-sm text-slate-700 transition hover:bg-red-50 hover:text-red-700 lg:mt-6 lg:w-full lg:px-4 lg:py-3">Logout</button></nav>
   <footer className="hidden border-t border-slate-200 p-4 lg:block"><div className="rounded-lg border border-slate-200 bg-slate-50 p-4 shadow-sm"><div className="flex items-center gap-2"><span className="h-2 w-2 rounded-full bg-emerald-500"/><span className="text-xs font-semibold uppercase tracking-[.22em] text-emerald-700">Operational</span></div><div className="mt-3 text-sm font-bold text-slate-950">X2DHF SaaS</div><div className="mt-1 text-xs leading-5 text-slate-600">Free scientific workspace for stored inputs, SCF runs, results, analytics, and account controls.</div><div className="mt-4 grid grid-cols-2 gap-2 text-xs"><NavLink to="/learn" className="rounded border border-slate-300 px-2 py-1 text-slate-700 hover:border-slate-950 hover:text-slate-950">Physics</NavLink><NavLink to="/results" className="rounded border border-slate-300 px-2 py-1 text-slate-700 hover:border-slate-950 hover:text-slate-950">Results</NavLink><NavLink to="/computations" className="rounded border border-slate-300 px-2 py-1 text-slate-700 hover:border-slate-950 hover:text-slate-950">Run</NavLink>{isAdmin?<NavLink to="/admin-dashboard" className="rounded border border-slate-300 px-2 py-1 text-slate-700 hover:border-slate-950 hover:text-slate-950">Admin</NavLink>:<NavLink to="/settings" className="rounded border border-slate-300 px-2 py-1 text-slate-700 hover:border-slate-950 hover:text-slate-950">Account</NavLink>}</div></div></footer>
  </aside>
  <main className="relative flex-1 overflow-x-hidden bg-slate-50"><div className="relative min-h-screen p-4 sm:p-6 lg:p-8"><Outlet/></div><footer className="relative border-t border-slate-200 bg-white px-4 py-6 text-xs text-slate-600 sm:px-6 lg:px-8"><div className="mx-auto grid max-w-7xl gap-4 md:grid-cols-[1fr_auto] md:items-center"><div><div className="font-semibold text-slate-950">X2DHF Scientific Cloud Workspace</div><div className="mt-1 max-w-2xl leading-5">Python runtime for guided HF/DFT workflows. Outputs, inputs, audit events, and scientific results are stored per user.</div></div><div className="flex flex-wrap gap-2"><NavLink to="/learn" className="rounded border border-slate-300 px-3 py-1.5 hover:border-slate-950 hover:text-slate-950">Docs</NavLink><NavLink to="/settings" className="rounded border border-slate-300 px-3 py-1.5 hover:border-slate-950 hover:text-slate-950">Account</NavLink>{isAdmin&&<NavLink to="/admin-dashboard" className="rounded border border-slate-300 px-3 py-1.5 hover:border-slate-950 hover:text-slate-950">Admin</NavLink>}<span className="rounded border border-slate-200 px-3 py-1.5 text-slate-500">2026</span></div></div></footer></main>
 </div>;
};

export default Layout;
