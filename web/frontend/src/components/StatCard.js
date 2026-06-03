import React from 'react';

const tones={
 blue:'from-blue-50 via-white to-white border-blue-200 text-blue-700',
 emerald:'from-emerald-50 via-white to-white border-emerald-200 text-emerald-700',
 amber:'from-amber-50 via-white to-white border-amber-200 text-amber-700',
 rose:'from-rose-50 via-white to-white border-rose-200 text-rose-700',
 slate:'from-slate-50 via-white to-white border-slate-200 text-slate-700'
};

const StatCard=({label,value,tone='slate'})=>{
 return <div className={`metric-card rounded-lg border bg-gradient-to-br ${tones[tone]||tones.slate} p-6 shadow-sm`}>
  <div className="flex items-start justify-between gap-3">
   <h3 className="text-xs font-semibold uppercase tracking-[.22em] text-slate-500">{label}</h3>
   <span className="h-2 w-2 rounded-full bg-current"/>
  </div>
  <p className="mt-4 text-5xl font-black tracking-tight text-slate-950">{value}</p>
  <div className="mt-5 h-1 overflow-hidden rounded-full bg-slate-200"><div className="h-full w-2/3 rounded-full bg-current opacity-80"/></div>
 </div>;
};

export default StatCard;
