import React from 'react';

const WorldMapBackdrop=()=>(
 <div className="pointer-events-none absolute inset-0 overflow-hidden bg-slate-950">
  <div className="world-map absolute inset-0 opacity-95"/>
  <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_20%,rgba(34,211,238,.22),transparent_30%),linear-gradient(180deg,rgba(2,6,23,.18),#020617_86%)]"/>
 </div>
);

export default WorldMapBackdrop;
