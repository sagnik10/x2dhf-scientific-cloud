import React,{useEffect,useState} from 'react';
import {computationAPI} from '../api/client';

const blocks=[
 {title:'Hartree-Fock',body:'Hartree-Fock approximates the many-electron wavefunction by orbitals. The runtime iterates orbital energies, Coulomb terms, exchange terms, and nuclear contributions until the SCF controls are satisfied.'},
 {title:'Density Functional Theory',body:'DFT replaces the full many-electron wavefunction with density-driven exchange-correlation terms. The functional selector is preserved in the input deck and used by the Python DFT energy model.'},
 {title:'SCF Iterations',body:'Self-consistent field iteration repeatedly updates orbital energies and potentials. You can set the maximum iteration count up to 10000 from the Computations form.'},
 {title:'Energy Components',body:'The output separates kinetic, nuclear attraction, Coulomb, exchange, correlation, nuclear repulsion, total electronic, and total energy values so results can be audited and exported.'},
 {title:'Custom Molecules',body:'Set ZA, ZB, distance R, charge, occupations, grid controls, and SCF controls directly. Samples from the original X2DHF test sets can be loaded and then edited through the form.'},
 {title:'Output Format',body:'The Python runtime emits an X2DHF-style listing: banner, echoed input, atomic system, method, electronic configuration, SCF table, energy components, orbital table, and CPU summary.'}
];

const Learn=()=>{
 const [science,setScience]=useState(null);
 useEffect(()=>{computationAPI.getScience().then(response=>setScience(response.data)).catch(()=>setScience(null));},[]);
 return(<div className="space-y-6 text-slate-100"><div><h1 className="text-4xl font-bold text-white">Physics and Mathematics</h1><p className="text-slate-400">A practical guide to the Python X2DHF SaaS runtime, inputs, and output interpretation.</p></div><div className="grid grid-cols-1 gap-4 lg:grid-cols-2">{blocks.map(block=><section key={block.title} className="rounded-lg border border-slate-800 bg-slate-950/80 p-5 shadow-xl"><h2 className="text-xl font-semibold text-cyan-100">{block.title}</h2><p className="mt-2 text-sm leading-6 text-slate-300">{block.body}</p></section>)}</div><section className="rounded-lg border border-slate-800 bg-slate-950/80 p-5 shadow-xl"><h2 className="text-xl font-semibold text-white">Input Cards</h2><div className="mt-4 grid grid-cols-1 gap-3 md:grid-cols-2">{Object.entries(science?.cards||{}).map(([key,value])=><div key={key} className="rounded border border-slate-800 bg-slate-900/70 p-3"><div className="font-mono text-cyan-100">{key}</div><div className="mt-1 text-sm text-slate-300">{value.meaning}</div><div className="mt-1 font-mono text-xs text-slate-500">{value.format}</div></div>)}</div></section><section className="rounded-lg border border-slate-800 bg-slate-950/80 p-5 shadow-xl"><h2 className="text-xl font-semibold text-white">Theory Modes</h2><div className="mt-4 grid grid-cols-1 gap-3 md:grid-cols-2">{Object.values(science?.theories||{}).map(item=><div key={item.name} className="rounded border border-slate-800 bg-slate-900/70 p-3"><div className="text-cyan-100">{item.name}</div><p className="mt-1 text-sm text-slate-300">{item.summary}</p></div>)}</div></section></div>);
};

export default Learn;
