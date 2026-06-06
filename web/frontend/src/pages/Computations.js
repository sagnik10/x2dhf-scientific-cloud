import React,{useEffect,useMemo,useState} from 'react';
import {useSearchParams} from 'react-router-dom';
import {useDispatch,useSelector} from 'react-redux';
import {computationAPI} from '../api/client';
import {fetchComputations,fetchSystems} from '../store/computationSlice';
import ComputationForm from '../components/ComputationForm';

const statusClass=status=>({completed:'bg-emerald-50 text-emerald-700 border-emerald-200',running:'bg-cyan-50 text-cyan-700 border-cyan-200',failed:'bg-rose-50 text-rose-700 border-rose-200',pending:'bg-amber-50 text-amber-700 border-amber-200'}[status]||'bg-slate-50 text-slate-700 border-slate-200');

const buildButtons=[
 {mode:'basic',label:'Build Native HF'},
 {mode:'libxc',label:'Build Native Libxc'},
 {mode:'openmp_libxc',label:'Build Native OpenMP'}
];
const windowsSetupCommands=[
 'wsl --install --no-distribution',
 'Restart Windows if prompted.',
 'wsl --install -d Ubuntu',
 'Launch Ubuntu once from Start Menu and create the Linux user.'
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
 const isWindows=nativeStatus?.os==='Windows';
 const wslReady=!!nativeStatus?.wsl?.ready;
 const pythonReady=!!nativeStatus?.python_runtime?.ready;
 const nativeReady=!!nativeStatus?.native_ready;
 const runtimeReady=!!nativeStatus?.ready||pythonReady;

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
  }).finally(()=>{setBuilding(false);loadNative();});
 };

 return(
  <div className="space-y-6 text-slate-900">
   <div className="flex flex-wrap items-center justify-between gap-4">
    <div>
     <h1 className="text-4xl font-bold text-slate-950">Computations</h1>
     <p className="mt-1 text-slate-600">Web-managed X2DHF finite-difference Hartree-Fock, HFS, OED, TED, SCMC, and DFT runtime.</p>
    </div>
    <button onClick={()=>setShowForm(!showForm)} className="rounded-lg bg-cyan-500 px-6 py-2 font-semibold text-white shadow-sm hover:bg-cyan-600">{showForm?'Hide Input':'New Computation'}</button>
   </div>

   {nativeStatus&&(
    <section className={`rounded-lg border bg-white p-5 shadow-sm ${runtimeReady?'border-emerald-200':'border-amber-200'}`}>
     <div className="flex flex-wrap items-start justify-between gap-4">
      <div>
       <h2 className="font-semibold text-slate-950">X2DHF Runtime</h2>
       <p className="mt-1 text-sm text-slate-600">{nativeStatus.message||'Checking native Fortran/C runtime'}</p>
       <div className="mt-3 grid grid-cols-1 gap-2 text-xs text-slate-600 md:grid-cols-3">
        <span>Executable native binaries: {(nativeStatus.compiled_binaries||[]).join(', ')||'none'}</span>
        <span>Fortran/C sources: {(nativeStatus.sources?.fortran?.count||0)+(nativeStatus.sources?.c?.count||0)}</span>
        <span>Sample inputs: {nativeStatus.sources?.inputs?.count||0}</span>
       </div>
      </div>
      <span className={`rounded-full border px-3 py-1 text-xs font-semibold ${runtimeReady?'border-emerald-200 bg-emerald-50 text-emerald-700':'border-amber-200 bg-amber-50 text-amber-700'}`}>{nativeReady?'native active':pythonReady?'python runtime active':'build required'}</span>
     </div>
     {nativeStatus&&(
      <div className="mt-4 space-y-3">
       <div className={`rounded border p-3 text-sm ${runtimeReady?'border-emerald-200 bg-emerald-50 text-emerald-800':'border-amber-200 bg-amber-50 text-amber-800'}`}>{nativeReady?'Jobs now run through the original X2DHF Fortran/C finite-difference engine on the server. Users only need the browser.':pythonReady?'Jobs can run now through the Python reference/replay runtime. Build native X2DHF later if you need the original Fortran/C solver for every case.':isWindows?'This Windows host needs a Linux runtime for the native solver. Use the setup buttons below, or deploy the app on a Linux/Docker server so all users can work from the browser.':'Build native X2DHF before submitting jobs. On a shared deployment this is done once in the Linux/Docker server image.'}</div>
       <div className="grid grid-cols-1 gap-3 text-sm md:grid-cols-3">
        <div className="rounded border border-slate-200 bg-slate-50 p-3"><div className="font-semibold text-slate-950">Recommended</div><p className="mt-1 text-slate-600">Deploy with Docker/Linux. The image builds X2DHF during setup and serves the app to every user.</p></div>
        <div className="rounded border border-slate-200 bg-slate-50 p-3"><div className="font-semibold text-slate-950">Windows Users</div><p className="mt-1 text-slate-600">Use the website from the browser. Native execution happens on the Linux backend, not on the Windows client.</p></div>
        <div className="rounded border border-slate-200 bg-slate-50 p-3"><div className="font-semibold text-slate-950">Local Dev</div><p className="mt-1 text-slate-600">Use Docker Desktop or WSL if you want to host the native runtime on your own machine.</p></div>
       </div>
       {isWindows&&!nativeReady&&<div className="rounded border border-blue-200 bg-blue-50 p-3 text-sm text-blue-800"><div className="font-semibold">Windows setup order</div><p className="mt-1">The website cannot enable Windows features, accept UAC prompts, restart Windows, or turn on BIOS virtualization. Do this prerequisite once, then the web app can install Linux packages and build native X2DHF.</p><ol className="mt-3 list-decimal space-y-1 pl-5">{windowsSetupCommands.map(item=><li key={item} className="font-mono text-xs text-blue-950">{item}</li>)}</ol><p className="mt-3 text-xs">Docker status: {nativeStatus.docker_available?'available on PATH':'not installed or not on PATH'}. WSL status: {wslReady?'Ubuntu ready':nativeStatus.wsl?.message||'not ready'}.</p></div>}
       {isWindows&&!nativeReady&&<div className="flex flex-wrap gap-2"><button disabled={building||!wslReady} title={!wslReady?'Finish the Administrator PowerShell WSL steps and launch Ubuntu once first.':'Install Linux build packages inside Ubuntu WSL.'} onClick={()=>startBuild('install_deps')} className="rounded-lg border border-blue-200 bg-blue-50 px-4 py-2 text-sm font-semibold text-blue-700 hover:bg-blue-100 disabled:cursor-not-allowed disabled:opacity-50">{building?'Working...':'Install Linux Deps'}</button></div>}
       <div className="flex flex-wrap gap-2">
        {buildButtons.map(item=>{const disabled=building||(isWindows&&!wslReady);return <button key={item.mode} disabled={disabled} title={isWindows&&!wslReady?'Install and open Ubuntu WSL first.':item.label} onClick={()=>startBuild(item.mode)} className="rounded-lg border border-cyan-200 bg-cyan-50 px-4 py-2 text-sm font-semibold text-cyan-700 hover:bg-cyan-100 disabled:cursor-not-allowed disabled:opacity-50">{building?'Building...':item.label}</button>;})}
       </div>
       <div className="rounded border border-slate-200 bg-slate-950 p-3 font-mono text-xs text-emerald-100">
        <div>Native build command: {nativeStatus.build_commands?.libxc}</div>
        {isWindows&&<div className="mt-1 text-cyan-100">Windows WSL setup: {nativeStatus.build_commands?.install_wsl}</div>}
        {!nativeStatus.docker_available&&<div className="mt-1 text-amber-100">Docker command skipped: docker is not installed or not on PATH.</div>}
       </div>
       {(nativeBuild?.error||nativeBuild?.build_error)&&<div className="whitespace-pre-wrap rounded border border-rose-200 bg-rose-50 p-3 text-sm text-rose-700">{nativeBuild.error||nativeBuild.build_error}</div>}
       {nativeBuild?.log&&<pre className="max-h-56 overflow-auto rounded border border-slate-200 bg-slate-950 p-3 font-mono text-xs text-slate-100">{nativeBuild.log}</pre>}
      </div>
     )}
    </section>
   )}

   {showForm&&<ComputationForm systems={systems} nativeReady={runtimeReady} onSubmitted={submitComplete} onClose={()=>{setShowForm(false);dispatch(fetchComputations());}}/>}
   <div className="flex flex-wrap gap-2">{['all','pending','running','completed','failed'].map(status=><button key={status} onClick={()=>changeFilter(status)} className={`rounded-lg border px-4 py-2 capitalize ${filterStatus===status?'border-cyan-500 bg-cyan-50 text-cyan-700':'border-slate-200 bg-white text-slate-700 hover:bg-slate-50'}`}>{status}</button>)}</div>
   <div className="grid grid-cols-1 gap-6 xl:grid-cols-2">
    <section className="overflow-hidden rounded-lg border border-slate-200 bg-white shadow-sm">
     <table className="w-full text-sm">
      <thead><tr className="bg-slate-100 text-slate-700"><th className="px-5 py-3 text-left">Title</th><th className="px-5 py-3 text-left">Theory</th><th className="px-5 py-3 text-left">Status</th><th className="px-5 py-3 text-left">Created</th></tr></thead>
      <tbody>{filtered.length?filtered.map(c=><tr key={c.id} onClick={()=>{setSelected(c);setRuntime(null);}} className={`cursor-pointer border-t border-slate-200 hover:bg-cyan-50 ${selected?.id===c.id?'bg-cyan-50':''}`}><td className="px-5 py-3 font-semibold text-slate-950">{c.title}</td><td className="px-5 py-3 uppercase text-slate-600">{c.theory}</td><td className="px-5 py-3"><span className={`rounded-full border px-3 py-1 text-xs font-semibold ${statusClass(c.status)}`}>{c.status}</span></td><td className="px-5 py-3 text-slate-500">{new Date(c.created_at).toLocaleString()}</td></tr>):<tr><td colSpan="4" className="px-5 py-10 text-center text-slate-500">No runs yet. Use the input runner above to load a sample or paste your own deck.</td></tr>}</tbody>
     </table>
    </section>
    <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
     <div className="mb-4 flex items-center justify-between">
      <div>
       <h2 className="text-xl font-semibold text-slate-950">Runtime Output</h2>
       <p className="text-sm text-slate-600">{selected?selected.title:'Submit a run to watch stdout/output here automatically.'}</p>
      </div>
      {current.status&&<span className={`rounded-full border px-3 py-1 text-xs font-semibold ${statusClass(current.status)}`}>{current.status}</span>}
     </div>
     {current.error_message&&<div className="mb-3 whitespace-pre-wrap rounded border border-rose-200 bg-rose-50 p-3 text-sm text-rose-700">{Array.isArray(current.error_message)?current.error_message.join('\n'):current.error_message}</div>}
     {['pending','running'].includes(current.status)&&<div className="mb-3 rounded-lg border border-cyan-200 bg-cyan-50 p-4"><div className="flex items-center justify-between gap-3"><div><div className="font-semibold text-cyan-800">SCF engine active</div><div className="text-xs text-slate-600">Long 50 lakh iteration runs remain live here while representative convergence rows stream into output.</div></div><div className="h-10 w-10 animate-spin rounded-full border-2 border-cyan-200 border-t-cyan-500"/></div><div className="mt-4 h-2 overflow-hidden rounded-full bg-slate-200"><div className="runtime-progress h-full rounded-full bg-gradient-to-r from-cyan-400 via-emerald-400 to-blue-500"/></div></div>}
     <pre className="h-[560px] overflow-auto rounded-lg border border-slate-200 bg-slate-950 p-4 font-mono text-xs leading-relaxed text-emerald-100">{current.output_log||current.error_message||'No runtime output yet.'}</pre>
    </section>
   </div>
  </div>
 );
};

export default Computations;
