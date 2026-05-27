import React from 'react';

const tones={
 blue:'from-blue-500/25 via-cyan-400/10 to-slate-950 border-cyan-300/20 text-cyan-100',
 emerald:'from-emerald-500/25 via-teal-400/10 to-slate-950 border-emerald-300/20 text-emerald-100',
 amber:'from-amber-400/25 via-orange-400/10 to-slate-950 border-amber-300/20 text-amber-100',
 rose:'from-rose-500/25 via-fuchsia-400/10 to-slate-950 border-rose-300/20 text-rose-100',
 slate:'from-slate-500/20 via-cyan-400/5 to-slate-950 border-slate-700 text-slate-100'
};

const StatCard=({label,value,tone='slate'})=>{
 return <div className={`metric-card rounded-lg border bg-gradient-to-br ${tones[tone]||tones.slate} p-6 shadow-2xl shadow-slate-950/40`}>
  <div className="flex items-start justify-between gap-3">
   <h3 className="text-xs font-semibold uppercase tracking-[.22em] text-white/55">{label}</h3>
   <span className="h-2 w-2 rounded-full bg-current shadow-[0_0_18px_currentColor]"/>
  </div>
  <p className="mt-4 text-5xl font-black tracking-tight text-white">{value}</p>
  <div className="mt-5 h-1 overflow-hidden rounded-full bg-white/10"><div className="h-full w-2/3 rounded-full bg-current opacity-80"/></div>
 </div>;
};

export default StatCard;
