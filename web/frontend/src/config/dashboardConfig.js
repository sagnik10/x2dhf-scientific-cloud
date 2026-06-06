import {useEffect,useMemo,useState} from 'react';

const themes={
 laboratory:{accent:'#1d4ed8',secondary:'#ea580c',surface:'bg-white',border:'border-slate-200',text:'text-slate-950',muted:'text-slate-600'},
 terminal:{accent:'#047857',secondary:'#0f766e',surface:'bg-slate-950',border:'border-emerald-400/20',text:'text-emerald-50',muted:'text-emerald-200/70'},
 print:{accent:'#334155',secondary:'#64748b',surface:'bg-white',border:'border-slate-300',text:'text-slate-950',muted:'text-slate-700'}
};

const fallback={theme:process.env.REACT_APP_DASHBOARD_THEME||'laboratory',title:'Quantum Runtime Dashboard',subtitle:'Live telemetry for native X2DHF finite-difference jobs, SCF convergence, stored results, and molecule experiments.'};

export function useDashboardConfig(){
 const [config,setConfig]=useState(fallback);
 useEffect(()=>{fetch('/dashboard.config.json',{cache:'no-store'}).then(response=>response.ok?response.json():fallback).then(data=>setConfig({...fallback,...data,theme:process.env.REACT_APP_DASHBOARD_THEME||data.theme||fallback.theme})).catch(()=>setConfig(fallback));},[]);
 return useMemo(()=>({...config,themeValues:themes[config.theme]||themes.laboratory}),[config]);
}
