import React,{useEffect,useState} from 'react';
import {useDispatch,useSelector} from 'react-redux';
import {fetchResults} from '../store/resultSlice';
import {computationAPI,resultAPI} from '../api/client';

const value=v=>v===null||v===undefined?'N/A':Number(v).toExponential(10);

const Results=()=>{
 const dispatch=useDispatch();
 const {results}=useSelector(state=>state.result);
 const [selected,setSelected]=useState(null);
 const [downloading,setDownloading]=useState(false);
 const [downloadingInput,setDownloadingInput]=useState(false);
 useEffect(()=>{dispatch(fetchResults());},[dispatch]);
 const active=selected||results[0];
 const components=active?.convergence_info?.energy_components||{};
 const orbitals=active?.convergence_info?.orbitals||[];
 const cards=active?.convergence_info?.input?.cards||[];
 const downloadRaw=async()=>{
  if(!active||downloading)return;
  setDownloading(true);
  try{
   const response=await resultAPI.downloadRaw(active.id);
   const disposition=response.headers['content-disposition']||'';
   const match=disposition.match(/filename="([^"]+)"/);
   const fallback=`${(active.computation?.title||'x2dhf-result').replace(/[^a-z0-9_-]+/gi,'_')}_${active.id}.lst`;
   const url=window.URL.createObjectURL(response.data);
   const link=document.createElement('a');
   link.href=url;
   link.download=match?.[1]||fallback;
   document.body.appendChild(link);
   link.click();
   link.remove();
   window.URL.revokeObjectURL(url);
  }finally{
   setDownloading(false);
  }
 };
 const downloadInput=async()=>{
  if(!active?.computation?.id||downloadingInput)return;
  setDownloadingInput(true);
  try{
   const response=await computationAPI.downloadInput(active.computation.id);
   const disposition=response.headers['content-disposition']||'';
   const match=disposition.match(/filename="([^"]+)"/);
   const fallback=`${(active.computation?.title||'x2dhf-input').replace(/[^a-z0-9_-]+/gi,'_')}_${active.computation.id}.data`;
   const url=window.URL.createObjectURL(response.data);
   const link=document.createElement('a');
   link.href=url;
   link.download=match?.[1]||fallback;
   document.body.appendChild(link);
   link.click();
   link.remove();
   window.URL.revokeObjectURL(url);
  }finally{
   setDownloadingInput(false);
  }
 };
 return(<div className="space-y-6 text-slate-900"><div className="flex flex-wrap items-end justify-between gap-3"><div><h1 className="text-4xl font-bold text-slate-950">Scientific Results</h1><p className="text-slate-600">Parsed energies, orbitals, input meanings, and saved X2DHF-style output.</p></div>{active&&<div className="flex flex-wrap gap-2"><button onClick={downloadInput} disabled={downloadingInput} className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-bold text-slate-950 shadow-sm transition hover:border-slate-950 disabled:cursor-wait disabled:opacity-60">{downloadingInput?'Preparing...':'Download input'}</button><button onClick={downloadRaw} disabled={downloading} className="rounded-lg border border-slate-950 bg-slate-950 px-4 py-2 text-sm font-bold text-white shadow-sm transition hover:bg-white hover:text-slate-950 disabled:cursor-wait disabled:opacity-60">{downloading?'Preparing...':'Download .lst'}</button></div>}</div><div className="grid grid-cols-1 gap-6 xl:grid-cols-3"><section className="overflow-hidden rounded-lg border border-slate-200 bg-white xl:col-span-1"><table className="w-full text-sm"><thead><tr className="bg-slate-100 text-slate-700"><th className="px-4 py-3 text-left">Computation</th><th className="px-4 py-3 text-left">Energy</th></tr></thead><tbody>{results.map(r=><tr key={r.id} onClick={()=>setSelected(r)} className="cursor-pointer border-t border-slate-200 hover:bg-slate-50"><td className="px-4 py-3 text-slate-950">{r.computation.title}<div className="text-xs uppercase text-slate-500">{r.computation.theory}</div></td><td className="px-4 py-3 font-mono text-blue-700">{value(r.total_energy)}</td></tr>)}</tbody></table></section><section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm xl:col-span-2">{active?<div className="space-y-6"><div><h2 className="text-2xl font-bold text-slate-950">{active.computation.title}</h2><p className="text-sm text-slate-600">Output parsed from the stored science listing.</p></div><div className="grid grid-cols-1 gap-3 md:grid-cols-3"><div className="rounded border border-slate-200 bg-slate-50 p-3"><div className="text-xs text-slate-500">Total energy</div><div className="font-mono text-blue-700">{value(active.total_energy)}</div></div><div className="rounded border border-slate-200 bg-slate-50 p-3"><div className="text-xs text-slate-500">Kinetic energy</div><div className="font-mono text-blue-700">{value(active.kinetic_energy||components.kinetic_energy)}</div></div><div className="rounded border border-slate-200 bg-slate-50 p-3"><div className="text-xs text-slate-500">Exchange energy</div><div className="font-mono text-blue-700">{value(active.exchange_energy||components.exchange_energy)}</div></div></div><div><h3 className="mb-2 font-semibold text-slate-950">Energy Components</h3><div className="grid grid-cols-1 gap-2 md:grid-cols-2">{Object.entries(components).map(([key,val])=><div key={key} className="flex justify-between rounded border border-slate-200 bg-slate-50 px-3 py-2 text-sm"><span className="text-slate-700">{key.replaceAll('_',' ')}</span><span className="font-mono text-emerald-700">{typeof val==='number'?value(val):val}</span></div>)}</div></div><div><h3 className="mb-2 font-semibold text-slate-950">Orbitals</h3><table className="w-full border border-slate-200 text-sm"><thead><tr className="bg-slate-100 text-slate-700"><th className="p-2 text-left">#</th><th className="p-2 text-left">Symmetry</th><th className="p-2 text-left">Energy</th><th className="p-2 text-left">1-norm error</th></tr></thead><tbody>{orbitals.map(o=><tr key={o.index} className="border-t border-slate-200"><td className="p-2">{o.index}</td><td className="p-2">{o.symmetry}</td><td className="p-2 font-mono text-blue-700">{value(o.energy)}</td><td className="p-2 font-mono text-emerald-700">{value(o.norm_error)}</td></tr>)}</tbody></table></div><div><h3 className="mb-2 font-semibold text-slate-950">Input Meaning</h3><div className="max-h-64 overflow-auto rounded border border-slate-200 divide-y divide-slate-200">{cards.map(card=><div key={`${card.line}-${card.raw}`} className="p-3"><div className="font-mono text-sm text-blue-700">{card.raw}</div><div className="text-sm text-slate-600">{card.meaning}</div></div>)}</div></div><div><h3 className="mb-2 font-semibold text-slate-950">Raw Output</h3><pre className="max-h-96 overflow-auto rounded border border-slate-200 bg-slate-50 p-4 text-xs text-slate-950">{active.output_log}</pre></div></div>:<p className="text-slate-600">No results yet.</p>}</section></div></div>);
};

export default Results;
