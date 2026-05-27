import React,{useEffect,useState} from 'react';
import {useMutation,useQuery,useQueryClient} from 'react-query';
import {userAPI} from '../api/client';

const Settings=()=>{
 const queryClient=useQueryClient();
 const {data:profileResponse}=useQuery('profile',userAPI.getProfile);
 const profile=profileResponse?.data;
 const [formData,setFormData]=useState({first_name:'',last_name:'',organization:''});
 useEffect(()=>{if(profile)setFormData({first_name:profile.first_name||'',last_name:profile.last_name||'',organization:profile.profile?.organization||''});},[profile]);
 const updateMutation=useMutation(data=>userAPI.updateProfile(data),{onSuccess:()=>queryClient.invalidateQueries('profile')});
 const keyMutation=useMutation(()=>userAPI.generateApiKey(),{onSuccess:()=>queryClient.invalidateQueries('profile')});
 const handleChange=e=>setFormData({...formData,[e.target.name]:e.target.value});
 const handleSubmit=e=>{e.preventDefault();updateMutation.mutate(formData);};
 return(<div className="mx-auto max-w-3xl space-y-6 text-slate-100"><div><h1 className="text-4xl font-bold text-white">Settings</h1><p className="text-slate-400">Profile details and programmatic API access.</p></div><section className="rounded-lg border border-slate-800 bg-slate-950/80 p-6 shadow-xl"><h2 className="text-2xl font-bold text-white">Profile</h2><form onSubmit={handleSubmit} className="mt-5 space-y-4"><input type="text" name="first_name" placeholder="First Name" value={formData.first_name} onChange={handleChange} className="w-full rounded-lg border border-slate-700 bg-slate-900 px-4 py-3 text-slate-100 outline-none focus:border-cyan-400"/><input type="text" name="last_name" placeholder="Last Name" value={formData.last_name} onChange={handleChange} className="w-full rounded-lg border border-slate-700 bg-slate-900 px-4 py-3 text-slate-100 outline-none focus:border-cyan-400"/><input type="text" name="organization" placeholder="Organization" value={formData.organization} onChange={handleChange} className="w-full rounded-lg border border-slate-700 bg-slate-900 px-4 py-3 text-slate-100 outline-none focus:border-cyan-400"/><button type="submit" disabled={updateMutation.isLoading} className="rounded-lg bg-cyan-400 px-6 py-2 font-semibold text-slate-950 hover:bg-cyan-300 disabled:bg-slate-700 disabled:text-slate-400">{updateMutation.isLoading?'Updating...':'Update Profile'}</button>{updateMutation.isSuccess&&<span className="ml-3 text-sm text-emerald-300">Saved</span>}</form></section><section className="rounded-lg border border-slate-800 bg-slate-950/80 p-6 shadow-xl"><h2 className="text-2xl font-bold text-white">API Key</h2><p className="mt-2 text-slate-400">Use this key for scripts and external clients that call the X2DHF API.</p><div className="mt-4 overflow-auto rounded-lg border border-slate-800 bg-black p-4"><code className="break-all font-mono text-sm text-emerald-100">{profile?.profile?.api_key||'No API key generated'}</code></div><button onClick={()=>keyMutation.mutate()} disabled={keyMutation.isLoading} className="mt-4 rounded-lg bg-cyan-400 px-6 py-2 font-semibold text-slate-950 hover:bg-cyan-300 disabled:bg-slate-700 disabled:text-slate-400">{keyMutation.isLoading?'Generating...':'Generate New Key'}</button></section></div>);
};

export default Settings;
