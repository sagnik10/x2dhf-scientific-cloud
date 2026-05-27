import React,{useEffect,useMemo,useState} from 'react';
import {useSearchParams} from 'react-router-dom';
import {useDispatch,useSelector} from 'react-redux';
import {computationAPI} from '../api/client';
import {fetchComputations,fetchSystems} from '../store/computationSlice';
import ComputationForm from '../components/ComputationForm';

const statusClass=status=>({completed:'bg-emerald-400/10 text-emerald-200 border-emerald-400/20',running:'bg-cyan-400/10 text-cyan-200 border-cyan-400/20',failed:'bg-rose-400/10 text-rose-200 border-rose-400/20',pending:'bg-amber-400/10 text-amber-200 border-amber-400/20'}[status]||'bg-slate-400/10 text-slate-200 border-slate-400/20');

const buildButtons=[
 {mode:'basic',label:'Optional Native HF'},
 {mode:'libxc',label:'Optional Native Libxc'},
 {mode:'openmp_libxc',label:'Optional Native OpenMP'}
];

const Computations=()=>{
 const dispatch=useDispatch();
 const [searchParams,setSearchParams]=useSearchParams();
 const {computations,systems}=useSelector(state=>state.computation);
 const [showForm,setShowForm]=useState(true);
 const filterStatus=['all','pending','running','completed','failed'].includes(searchParams.get('status'))?searchParams.get('status'):'all';
 const [selected,setSelected]=useState(null);
 const [runtime,setRuntime]=useState(null);
 const [nativeStatus,setNativeStatus]=useState(null);
 const [nativeBuild,setNativeBuild]=useState(null);
 const [building,setBuilding]=useState(false);

 const loadNative=()=>{
  computationAPI.getNativeStatus().then(response=>setNativeStatus(response.data)).catch(()=>setNativeStatus(null));
  computationAPI.getNativeBuild().then(response=>setNativeBuild(response.data)).catch(()=>setNativeBuild(null));
 };

 useEffect(()=>{dispatch(fetchComputations());dispatch(fetchSystems());loadNative();},[dispatch]);
 useEffect(()=>{if(computations.length===0)setShowForm(true);},[computations.length]);
 useEffect(()=>{const active=computations.some(c=>['pending','running'].includes(c.status));const timer=setInterval(()=>{if(active)dispatch(fetchComputations());},3000);return()=>clearInterval(timer);},[computations,dispatch]);
 useEffect(()=>{if(!selected)return;let alive=true;const load=()=>computationAPI.getRuntimeOutput(selected.id).then(response=>{if(alive)setRuntime(response.data);}).catch(()=>{});load();const timer=setInterval(load,2000);return()=>{alive=false;clearInterval(timer);};},[selected]);
 useEffect(()=>{if(!building)return;const timer=setInterval(()=>{computationAPI.getNativeBuild().then(response=>{setNativeBuild(response.data);setNativeStatus(response.data);if(response.data.ready||!response.data.build_running)setBuilding(false);}).catch(()=>setBuilding(false));},3000);return()=>clearInterval(timer);},[building]);

 const filtered=useMemo(()=>filterStatus==='all'?computations:computations.filter(c=>c.status===filterStatus),[computations,filterStatus]);
 const current=runtime||{};
 const changeFilter=status=>setSearchParams(status==='all'?{}:{status});
 const submitComplete=job=>{setSelected(job);setRuntime({id:job.id,status:job.status,error_message:'',output_log:'Starting runtime...'});changeFilter('all');setTimeout(()=>{dispatch(fetchComputations());computationAPI.getRuntimeOutput(job.id).then(response=>setRuntime(response.data)).catch(()=>{});},700);};
 const startBuild=mode=>{
  setBuilding(true);
  computationAPI.startNativeBuild(mode).then(response=>setNativeBuild(response.data)).catch(error=>{
   const data=error.response?.data||{error:error.message};
   setNativeBuild(data);
   setBuilding(false);
  }).finally(loadNative);
 };

 return(
  <div className="space-y-6 text-slate-100">
   <div className="flex flex-wrap items-center justify-between gap-4">
    <div>
     <h1 className="text-4xl font-bold text-white">Computations</h1>
     <p className="text-slate-400">Python-first Hartree-Fock, HFS, OED, Quantum Espresso-style, and DFT runtime.</p>
    </div>
    <button onClick={()=>setShowForm(!showForm)} className="rounded-lg bg-cyan-400 px-6 py-2 font-semibold text-slate-950 hover:bg-cyan-300">{showForm?'Hide Input':'New Computation'}</button>
   </div>

   {nativeStatus&&(
    <section className={`rounded-lg border p-4 ${nativeStatus.ready?'border-emerald-400/20 bg-emerald-950/20':'border-amber-400/25 bg-amber-950/20'}`}>
     <div className="flex flex-wrap items-start justify-between gap-4">
      <div>
       <h2 className="font-semibold text-white">Python Science Runtime</h2>
       <p className="mt-1 text-sm text-slate-300">{nativeStatus.python_runtime?.message||'Python runtime ready'}</p>
       <div className="mt-2 grid grid-cols-1 gap-2 text-xs text-slate-400 md:grid-cols-3">
        <span>Engine: {nativeStatus.python_runtime?.engine||'python_science'}</span>
        <span>Native reference sources: {(nativeStatus.sources?.fortran?.count||0)+(nativeStatus.sources?.c?.count||0)}</span>
        <span>Sample inputs: {nativeStatus.sources?.inputs?.count||0}</span>
       </div>
      </div>
      <span className="rounded-full border border-emerald-400/30 px-3 py-1 text-xs font-semibold text-emerald-200">python ready</span>
     </div>
     {nativeStatus&&(
      <div className="mt-4 space-y-3">
       <div className="rounded border border-emerald-400/20 bg-emerald-500/10 p-3 text-sm text-emerald-100">Normal jobs run in Python. Native build buttons are optional and only for comparing against the original reference implementation.</div>
       <div className="flex flex-wrap gap-2">
        {buildButtons.map(item=><button key={item.mode} disabled={building} onClick={()=>startBuild(item.mode)} className="rounded-lg border border-cyan-300/30 bg-cyan-400/10 px-4 py-2 text-sm font-semibold text-cyan-100 hover:bg-cyan-400/20 disabled:cursor-not-allowed disabled:opacity-50">{building?'Building...':item.label}</button>)}
       </div>
       <div className="rounded border border-slate-800 bg-black p-3 font-mono text-xs text-emerald-100">
        <div>Python runtime is primary. Optional native reference command: {nativeStatus.build_commands?.libxc}</div>
       </div>
       {(nativeBuild?.error||nativeBuild?.build_error)&&<div className="whitespace-pre-wrap rounded border border-rose-400/30 bg-rose-500/10 p-3 text-sm text-rose-100">{nativeBuild.error||nativeBuild.build_error}</div>}
       {nativeBuild?.log&&<pre className="max-h-56 overflow-auto rounded border border-slate-800 bg-black p-3 font-mono text-xs text-slate-200">{nativeBuild.log}</pre>}
      </div>
     )}
    </section>
   )}

   {showForm&&<ComputationForm systems={systems} nativeReady={!!nativeStatus?.python_runtime?.ready} onSubmitted={submitComplete} onClose={()=>{setShowForm(false);dispatch(fetchComputations());}}/>}
   <div className="flex flex-wrap gap-2">{['all','pending','running','completed','failed'].map(status=><button key={status} onClick={()=>changeFilter(status)} className={`rounded-lg border px-4 py-2 capitalize ${filterStatus===status?'border-cyan-300 bg-cyan-300/10 text-cyan-100':'border-slate-700 bg-slate-900 text-slate-300 hover:bg-slate-800'}`}>{status}</button>)}</div>
   <div className="grid grid-cols-1 gap-6 xl:grid-cols-2">
    <section className="overflow-hidden rounded-lg border border-slate-800 bg-slate-950/80 shadow-xl">
     <table className="w-full text-sm">
      <thead><tr className="bg-slate-900 text-slate-300"><th className="px-5 py-3 text-left">Title</th><th className="px-5 py-3 text-left">Theory</th><th className="px-5 py-3 text-left">Status</th><th className="px-5 py-3 text-left">Created</th></tr></thead>
      <tbody>{filtered.length?filtered.map(c=><tr key={c.id} onClick={()=>{setSelected(c);setRuntime(null);}} className={`cursor-pointer border-t border-slate-800 hover:bg-cyan-400/5 ${selected?.id===c.id?'bg-cyan-400/10':''}`}><td className="px-5 py-3 text-white">{c.title}</td><td className="px-5 py-3 uppercase text-slate-300">{c.theory}</td><td className="px-5 py-3"><span className={`rounded-full border px-3 py-1 text-xs font-semibold ${statusClass(c.status)}`}>{c.status}</span></td><td className="px-5 py-3 text-slate-400">{new Date(c.created_at).toLocaleString()}</td></tr>):<tr><td colSpan="4" className="px-5 py-10 text-center text-slate-400">No runs yet. Use the input runner above to load a sample or paste your own deck.</td></tr>}</tbody>
     </table>
    </section>
    <section className="rounded-lg border border-slate-800 bg-slate-950/80 p-5 shadow-xl">
     <div className="mb-4 flex items-center justify-between">
      <div>
       <h2 className="text-xl font-semibold text-white">Runtime Output</h2>
       <p className="text-sm text-slate-400">{selected?selected.title:'Submit a run to watch stdout/output here automatically.'}</p>
      </div>
      {current.status&&<span className={`rounded-full border px-3 py-1 text-xs font-semibold ${statusClass(current.status)}`}>{current.status}</span>}
     </div>
     {current.error_message&&<div className="mb-3 whitespace-pre-wrap rounded border border-rose-400/30 bg-rose-500/10 p-3 text-sm text-rose-100">{Array.isArray(current.error_message)?current.error_message.join('\n'):current.error_message}</div>}
     {['pending','running'].includes(current.status)&&<div className="mb-3 rounded-lg border border-cyan-300/20 bg-cyan-400/10 p-4"><div className="flex items-center justify-between gap-3"><div><div className="font-semibold text-cyan-100">SCF engine active</div><div className="text-xs text-slate-400">Long 50 lakh iteration runs remain live here while representative convergence rows stream into output.</div></div><div className="h-10 w-10 animate-spin rounded-full border-2 border-cyan-300/20 border-t-cyan-300"/></div><div className="mt-4 h-2 overflow-hidden rounded-full bg-slate-800"><div className="runtime-progress h-full rounded-full bg-gradient-to-r from-cyan-300 via-emerald-300 to-violet-300"/></div></div>}
     <pre className="h-[560px] overflow-auto rounded-lg border border-slate-800 bg-black p-4 font-mono text-xs leading-relaxed text-emerald-100">{current.output_log||current.error_message||'No runtime output yet.'}</pre>
    </section>
   </div>
  </div>
 );
};

export default Computations;
