import React from 'react';
const ComputationsList=({computations})=>{
 if(!computations.length)return <p className="text-slate-600">No actions yet. Start from Computations and run a sample input deck.</p>;
 return(<div className="space-y-2">{computations.map(c=>(<div key={c.id} className="flex items-center justify-between rounded-lg border border-slate-200 bg-white p-4"><div><p className="font-semibold text-slate-950">{c.title}</p><p className="text-sm text-slate-600">{c.theory} - {new Date(c.created_at).toLocaleDateString()}</p></div><span className={`rounded-full px-3 py-1 text-sm font-semibold ${c.status==='completed'?'bg-emerald-50 text-emerald-700':c.status==='running'?'bg-cyan-50 text-cyan-700':c.status==='failed'?'bg-rose-50 text-rose-700':'bg-amber-50 text-amber-700'}`}>{c.status}</span></div>))}</div>);
};
export default ComputationsList;
