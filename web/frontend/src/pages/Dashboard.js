import React,{useEffect,useMemo,useState} from 'react';
import {Link} from 'react-router-dom';
import {useDispatch,useSelector} from 'react-redux';
import {fetchSystems,fetchComputations} from '../store/computationSlice';
import {analyticsAPI} from '../api/client';
import StatCard from '../components/StatCard';
import ComputationsList from '../components/ComputationsList';
import {Area,AreaChart,Cell,Pie,PieChart,PolarAngleAxis,RadialBar,RadialBarChart,ResponsiveContainer,Tooltip,XAxis,YAxis} from 'recharts';

const theoryColors={hf:'#1d4ed8',dft:'#f97316',lda:'#facc15',hfs:'#22c55e',oed:'#ef4444',ted:'#f8fafc',scmc:'#7f1d1d',qe:'#064e3b'};
const theoryLabels={hf:'Hartree-Fock',dft:'DFT',lda:'LDA DFT',hfs:'HFS',oed:'OED',ted:'TED',scmc:'SCMC',qe:'Quantum Espresso'};

const Dashboard=()=>{
 const dispatch=useDispatch();
 const {systems,computations,loading}=useSelector(state=>state.computation);
 const [analytics,setAnalytics]=useState(null);
 useEffect(()=>{dispatch(fetchSystems());dispatch(fetchComputations());analyticsAPI.getUser().then(response=>setAnalytics(response.data)).catch(()=>setAnalytics(null));},[dispatch]);
 const stats=[
  {label:'Systems',value:analytics?.systems??systems.length,tone:'blue'},
  {label:'Completed',value:analytics?.completed??computations.filter(c=>c.status==='completed').length,tone:'emerald'},
  {label:'Running',value:analytics?.running??computations.filter(c=>c.status==='running').length,tone:'amber'},
  {label:'Failed',value:analytics?.failed??computations.filter(c=>c.status==='failed').length,tone:'rose'}
 ];
 const theoryData=(analytics?.by_theory||[]).map(item=>{const key=String(item.theory||'').toLowerCase();return {...item,key,label:theoryLabels[key]||String(item.theory||'Method').toUpperCase(),fill:theoryColors[key]||'#94a3b8'};});
 const totalRuns=analytics?.computations??computations.length;
 const completed=analytics?.completed??computations.filter(c=>c.status==='completed').length;
 const health=totalRuns?Math.round((completed/totalRuns)*100):0;
 const timeline=useMemo(()=>{const source=analytics?.activity||[];return source.length?source:[{day:'No runs',count:0}];},[analytics]);
 return <div className="space-y-6 text-slate-100">
  <section className="hero-console rounded-lg border border-cyan-300/10 bg-slate-950/70 p-7 shadow-2xl shadow-cyan-950/20">
   <div className="flex flex-wrap items-center justify-between gap-4"><div><div className="mb-2 font-mono text-xs uppercase tracking-[.35em] text-cyan-300/70">Python X2DHF Command Deck</div><h1 className="text-4xl font-black tracking-tight text-white">Quantum Runtime Dashboard</h1><p className="mt-2 max-w-2xl text-slate-400">Live scientific telemetry for HF, DFT, Libxc-style inputs, SCF convergence, stored results, and molecule experiments.</p></div><div className="flex flex-wrap items-center gap-3"><div className="rounded-full border border-cyan-300/20 bg-cyan-400/10 px-4 py-2 text-sm text-cyan-100">{Math.round(analytics?.cpu_time_seconds||0)} CPU seconds used</div><Link to="/computations" className="rounded-lg bg-cyan-300 px-5 py-2 font-bold text-slate-950 shadow-lg shadow-cyan-500/20 transition hover:-translate-y-0.5 hover:bg-white">Run Input</Link></div></div>
  </section>
  <div className="grid grid-cols-1 gap-4 md:grid-cols-4">{stats.map(stat=><StatCard key={stat.label} label={stat.label} value={stat.value} tone={stat.tone}/>)}</div>
  <div className="grid grid-cols-1 gap-6 2xl:grid-cols-3">
   <section className="glass-panel rounded-lg border border-cyan-300/10 bg-slate-950/80 p-6 shadow-2xl shadow-slate-950/50">
    <h2 className="mb-4 text-xl font-bold text-white">Runtime Health</h2>
    <div className="h-72"><ResponsiveContainer width="100%" height="100%"><RadialBarChart innerRadius="72%" outerRadius="100%" data={[{name:'completed',value:health,fill:'#22c55e'}]} startAngle={90} endAngle={-270}><PolarAngleAxis type="number" domain={[0,100]} tick={false}/><RadialBar dataKey="value" cornerRadius={16}/><text x="50%" y="45%" textAnchor="middle" dominantBaseline="middle" fill="#fff" fontSize="42" fontWeight="900">{health}%</text><text x="50%" y="59%" textAnchor="middle" dominantBaseline="middle" fill="#94a3b8" fontSize="13">completed runs</text></RadialBarChart></ResponsiveContainer></div>
   </section>
   <section className="glass-panel rounded-lg border border-cyan-300/10 bg-slate-950/80 p-6 shadow-2xl shadow-slate-950/50">
    <h2 className="mb-4 text-xl font-bold text-white">Theory Distribution</h2>
    <div className="h-72">{theoryData.length?<ResponsiveContainer width="100%" height="100%"><PieChart><Tooltip content={({active,payload})=>active&&payload?.length?<div className="rounded-lg border border-white/15 bg-slate-950 px-3 py-2 text-sm text-white shadow-xl shadow-slate-950/40"><div className="font-semibold">{payload[0].payload.label}</div><div className="text-slate-300">runs: {payload[0].value}</div></div>:null}/><Pie data={theoryData} dataKey="count" nameKey="label" innerRadius={64} outerRadius={104} paddingAngle={5}>{theoryData.map((entry,index)=><Cell key={entry.key||index} fill={entry.fill} stroke="#020617" strokeWidth={3}/>)}</Pie></PieChart></ResponsiveContainer>:<div className="flex h-full items-center justify-center rounded-lg border border-dashed border-cyan-300/15 text-slate-500">Run a computation to populate analytics.</div>}</div>
    <div className="mt-3 grid grid-cols-1 gap-2 sm:grid-cols-2">{theoryData.map(item=><div key={item.key} className="flex items-center justify-between rounded-lg border border-slate-800 bg-slate-900/60 px-3 py-2 text-xs"><span className="flex items-center gap-2 text-slate-200"><span className="h-3 w-3 rounded-full border border-white/20" style={{background:item.fill}}/>{item.label}</span><span className="font-mono text-slate-400">{item.count}</span></div>)}</div>
   </section>
   <section className="glass-panel rounded-lg border border-blue-500/20 bg-[radial-gradient(circle_at_top_right,rgba(249,115,22,.16),transparent_34%),linear-gradient(135deg,rgba(15,23,42,.92),rgba(2,6,23,.98))] p-6 shadow-2xl shadow-slate-950/50">
    <div className="mb-4 flex flex-wrap items-start justify-between gap-3"><div><div className="font-mono text-[11px] uppercase tracking-[.28em] text-orange-300/80">Run telemetry</div><h2 className="mt-1 text-xl font-black text-white">Activity Wave</h2></div><div className="flex gap-2 text-xs"><span className="rounded-full border border-blue-400/25 bg-blue-500/10 px-3 py-1 text-blue-100">{timeline.reduce((sum,item)=>sum+Number(item.count||0),0)} runs</span><span className="rounded-full border border-orange-400/25 bg-orange-500/10 px-3 py-1 text-orange-100">{timeline.length} days</span></div></div>
    <div className="h-72"><ResponsiveContainer width="100%" height="100%"><AreaChart data={timeline} margin={{top:10,right:10,left:-18,bottom:0}}><defs><linearGradient id="activityWave" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#f97316" stopOpacity=".62"/><stop offset="42%" stopColor="#1d4ed8" stopOpacity=".32"/><stop offset="100%" stopColor="#020617" stopOpacity="0"/></linearGradient><filter id="waveGlow"><feGaussianBlur stdDeviation="3" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs><XAxis dataKey="day" stroke="#94a3b8" tick={{fontSize:11,fill:'#94a3b8'}} axisLine={{stroke:'#334155'}} tickLine={false}/><YAxis allowDecimals={false} stroke="#94a3b8" tick={{fontSize:11,fill:'#94a3b8'}} axisLine={false} tickLine={false}/><Tooltip content={({active,payload,label})=>active&&payload?.length?<div className="rounded-lg border border-orange-300/25 bg-slate-950/95 px-3 py-2 text-sm shadow-2xl"><div className="font-semibold text-white">{label}</div><div className="text-orange-200">{payload[0].value} runs submitted</div></div>:null}/><Area type="monotone" dataKey="count" stroke="#ffffff" strokeWidth={3} fill="url(#activityWave)" dot={{r:4,stroke:'#f97316',strokeWidth:2,fill:'#020617'}} activeDot={{r:7,stroke:'#ffffff',strokeWidth:2,fill:'#f97316'}} filter="url(#waveGlow)"/></AreaChart></ResponsiveContainer></div>
   </section>
  </div>
  <section className="glass-panel rounded-lg border border-cyan-300/10 bg-slate-950/80 p-6 shadow-2xl shadow-slate-950/50"><h2 className="mb-4 text-xl font-bold text-white">Recent Actions</h2>{loading?<p className="text-slate-400">Loading...</p>:<ComputationsList computations={computations.slice(0,6)}/>}</section>
 </div>;
};

export default Dashboard;
