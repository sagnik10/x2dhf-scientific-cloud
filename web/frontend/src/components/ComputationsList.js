import React from 'react';
const ComputationsList=({computations})=>{
 if(!computations.length)return <p className="text-slate-400">No actions yet. Start from Computations and run a sample input deck.</p>;
 return(<div className="space-y-2">{computations.map(c=>(<div key={c.id} className="flex items-center justify-between rounded-lg border border-slate-800 bg-slate-900/70 p-4"><div><p className="font-semibold text-white">{c.title}</p><p className="text-sm text-slate-400">{c.theory} - {new Date(c.created_at).toLocaleDateString()}</p></div><span className={`rounded-full px-3 py-1 text-sm font-semibold ${c.status==='completed'?'bg-emerald-400/10 text-emerald-200':c.status==='running'?'bg-cyan-400/10 text-cyan-200':c.status==='failed'?'bg-rose-400/10 text-rose-200':'bg-amber-400/10 text-amber-200'}`}>{c.status}</span></div>))}</div>);
};
export default ComputationsList;
