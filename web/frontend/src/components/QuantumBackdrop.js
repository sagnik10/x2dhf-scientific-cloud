import React from 'react';
import WorldMapBackdrop from './WorldMapBackdrop';

const QuantumBackdrop=()=>(
 <div className="absolute inset-0 overflow-hidden">
  <WorldMapBackdrop/>
  <div className="quantum-field absolute inset-0">
   <span/><span/><span/><span/><span/><span/>
  </div>
  <div className="quantum-orbit absolute left-1/2 top-1/2 h-72 w-72 -translate-x-1/2 -translate-y-1/2 opacity-50"/>
 </div>
);

export default QuantumBackdrop;
