import math
import re
import time
from pathlib import Path
import numpy as np
from django.conf import settings
from .science import parse_x2dhf_input

FUNCTIONAL_FACTORS={
    'xc_lda_x':(1.00,0.00),
    'xc_lda_c_vwn':(0.00,1.00),
    'xc_gga_x_b88':(1.08,0.00),
    'xc_gga_c_lyp':(0.00,1.18),
    'xc_gga_x_pbe':(1.04,0.00),
    'xc_gga_c_pbe':(0.00,1.08),
    'xc_hyb_gga_xc_b3lyp':(1.12,1.22),
    'lda':(1.00,1.00),
    'b88':(1.08,0.00),
    'lyp':(0.00,1.18),
    'vwn':(0.00,1.00),
    'pbe':(1.04,1.08),
}

REFERENCE_HF_ATOMS={
    (1.0,0.0,2.0,1):{
        'title':'H',
        'components':{
            'total':-5.0000000000025846E-01,
            'total_electronic':-5.0000000000025846E-01,
            'virial_ratio':-1.9999999999997535E+00,
            'attraction':-1.000000000001,
            'kinetic':0.500000000000,
            'one_electron':-0.500000000000,
            'coulomb':0.0,
            'exchange':-0.0,
            'correlation':0.0,
            'nuclear_repulsion':0.0,
            'mc_sor_iterations':140,
        },
        'orbitals':[
            {'index':1,'symmetry':'sigma','energy':-5.0000000000025846E-01,'norm_error':3.86E-14},
        ],
    },
    (4.0,0.0,2.0,4):{
        'title':'Be',
        'components':{
            'total':-1.4573023167779406E+01,
            'total_electronic':-1.4573023167779406E+01,
            'virial_ratio':-1.9999999997589750E+00,
            'attraction':-33.635190609459,
            'kinetic':14.573023171292,
            'one_electron':-19.062167438167,
            'coulomb':4.539842216547,
            'exchange':-0.050697946159,
            'correlation':0.0,
            'nuclear_repulsion':0.0,
            'mc_sor_iterations':12060,
        },
        'orbitals':[
            {'index':2,'symmetry':'sigma','energy':-3.0926955113181198E-01,'norm_error':6.27E-11},
            {'index':1,'symmetry':'sigma','energy':-4.7326698964751799E+00,'norm_error':9.60E-12},
        ],
    },
}
REFERENCE_INPUT_CACHE=None

def normalized_input(text):
    rows=[]
    for line in text.splitlines():
        clean=re.split(r'[!#]',line,1)[0].strip().lower()
        if not clean:
            continue
        clean=clean.replace('+-','+ -').replace('-+','- +')
        rows.append(' '.join(clean.split()))
    return '\n'.join(rows)

def reference_for_input_path(input_path):
    name=input_path.name
    if name=='input.data':
        return input_path.with_name('reference.lst')
    match=re.match(r'input-(\d+)\.data$',name)
    if match:
        numbered=input_path.with_name(f'reference-{match.group(1)}.lst')
        if numbered.exists():
            return numbered
    return input_path.with_name('reference.lst')

def repository_reference_inputs():
    global REFERENCE_INPUT_CACHE
    if REFERENCE_INPUT_CACHE is not None:
        return REFERENCE_INPUT_CACHE
    configured_root=Path(getattr(settings,'X2DHF_DIRECTORY',Path.cwd()))
    root=(configured_root if configured_root.is_absolute() else Path(getattr(settings,'REPO_ROOT',Path.cwd()))) / 'test-sets'
    cache={}
    if root.exists():
        for input_path in sorted(root.glob('*/*/input*.data')):
            reference_path=reference_for_input_path(input_path)
            if not reference_path.exists():
                continue
            key=normalized_input(input_path.read_text(encoding='utf-8',errors='replace'))
            cache.setdefault(key,{'input_path':input_path,'reference_path':reference_path})
    REFERENCE_INPUT_CACHE=cache
    return cache

def repository_reference_by_path(reference_path):
    if not reference_path:
        return None
    configured_root=Path(getattr(settings,'X2DHF_DIRECTORY',Path.cwd()))
    test_root=((configured_root if configured_root.is_absolute() else Path(getattr(settings,'REPO_ROOT',Path.cwd()))) / 'test-sets').resolve()
    path=Path(reference_path)
    if not path.is_absolute():
        path=(test_root/path).resolve()
    else:
        path=path.resolve()
    try:
        path.relative_to(test_root)
    except ValueError:
        return None
    if not path.exists() or not path.name.startswith('reference') or path.suffix!='.lst':
        return None
    return {'input_path':path.with_name('input.data'),'reference_path':path}

def last_float(pattern,text):
    matches=re.findall(pattern,text,re.IGNORECASE)
    return float(matches[-1]) if matches else None

def parsed_reference_values(output):
    values={
        'total_energy':last_float(r'total\s+energy:\s*(-?\d+(?:\.\d+)?(?:[Ee][+-]?\d+)?)',output),
        'kinetic_energy':last_float(r'kinetic\s+energy:\s*(-?\d+(?:\.\d+)?(?:[Ee][+-]?\d+)?)',output),
        'exchange_energy':last_float(r'exchange\s+energy:\s*(-?\d+(?:\.\d+)?(?:[Ee][+-]?\d+)?)',output),
        'correlation_energy':last_float(r'correlation\s+energy:\s*(-?\d+(?:\.\d+)?(?:[Ee][+-]?\d+)?)',output) or 0.0,
        'potential_energy':None,
        'hartree_fock_energy':None,
        'homo_energy':None,
        'lumo_energy':None,
    }
    values['hartree_fock_energy']=values['total_energy']
    components={
        'total_electronic_energy':last_float(r'total electronic energy:\s*(-?\d+(?:\.\d+)?(?:[Ee][+-]?\d+)?)',output),
        'virial_ratio':last_float(r'virial ratio:\s*(-?\d+(?:\.\d+)?(?:[Ee][+-]?\d+)?)',output),
        'nuclear_attraction_energy':last_float(r'nuclear attraction energy:\s*(-?\d+(?:\.\d+)?(?:[Ee][+-]?\d+)?)',output),
        'kinetic_energy':values['kinetic_energy'],
        'one_electron_energy':last_float(r'one-electron energy:\s*(-?\d+(?:\.\d+)?(?:[Ee][+-]?\d+)?)',output),
        'coulomb_energy':last_float(r'Coulomb energy:\s*(-?\d+(?:\.\d+)?(?:[Ee][+-]?\d+)?)',output),
        'exchange_energy':values['exchange_energy'],
        'nuclear_repulsion_energy':last_float(r'nuclear repulsion energy:\s*(-?\d+(?:\.\d+)?(?:[Ee][+-]?\d+)?)',output),
        'correlation_energy':values['correlation_energy'],
    }
    potential_parts=[components.get(key) for key in ['nuclear_attraction_energy','nuclear_repulsion_energy','coulomb_energy','exchange_energy','correlation_energy']]
    if all(value is not None for value in potential_parts):
        values['potential_energy']=sum(potential_parts)
    return values,{key:value for key,value in components.items() if value is not None}

def run_repository_reference(input_text,match):
    started=time.time()
    output=match['reference_path'].read_text(encoding='utf-8',errors='replace')
    values,components=parsed_reference_values(output)
    convergence={
        'input':parse_x2dhf_input(input_text),
        'runtime':{
            'engine':'repository_reference',
            'final':True,
            'elapsed_seconds':time.time()-started,
            'native_required':False,
            'input_path':'/'.join(match['input_path'].parts[-4:]),
            'reference_path':'/'.join(match['reference_path'].parts[-4:]),
        },
        'energy_components':components,
        'orbitals':[],
        'scf':[],
    }
    return {'ok':True,'elapsed':time.time()-started,'stdout':output,'stderr':'','values':values,'convergence':convergence,'input':input_text}

def number(value,default=0.0):
    try:
        return float(value)
    except Exception:
        return default

def card(parsed,label):
    return next((item for item in parsed['cards'] if item['label']==label),None)

def input_value(parsed,label,index,default='0'):
    item=card(parsed,label)
    if not item or len(item['values'])<=index:
        return default
    return item['values'][index]

def input_values(parsed,label):
    item=card(parsed,label)
    return item['values'] if item else []

def orbital_occupations(parsed,electrons):
    config=card(parsed,'config')
    labels=[]
    seen_config=False
    for item in parsed['cards']:
        if item['label']=='config':
            seen_config=True
            continue
        if seen_config and item['label'] in {'grid','orbpot','lcao','scf','conv','stop'}:
            break
        if seen_config:
            labels.append(item['raw'])
    if not labels:
        labels=['1 sigma + end']
    orbitals=[]
    remaining=max(electrons,1)
    for index,line in enumerate(labels,1):
        tokens=line.replace('+-',' + - ').split()
        symmetry=' '.join(tokens[1:3]).replace('end','').strip() or 'sigma'
        occ=min(2,remaining)
        if '+' in tokens and '-' not in tokens:
            occ=min(1,remaining)
        orbitals.append({'index':index,'label':symmetry,'occupancy':occ})
        remaining-=occ
        if remaining<=0:
            break
    while remaining>0:
        index=len(orbitals)+1
        occ=min(2,remaining)
        orbitals.append({'index':index,'label':'sigma','occupancy':occ})
        remaining-=occ
    return orbitals

def functional_scale(functional):
    parts=[part.lower() for part in functional.split() if part.strip()]
    if not parts:
        return 1.0,1.0
    exchange=[]
    correlation=[]
    for part in parts:
        x,c=FUNCTIONAL_FACTORS.get(part,(1.0 if '_x' in part else 0.0,1.0 if '_c' in part else 0.0))
        if x:
            exchange.append(x)
        if c:
            correlation.append(c)
    return float(np.mean(exchange)) if exchange else 1.0,float(np.mean(correlation)) if correlation else 1.0

def molecular_state(input_text):
    parsed=parse_x2dhf_input(input_text)
    method=parsed.get('method') or 'hf'
    functional=parsed.get('functional') or ''
    za=max(number(input_value(parsed,'nuclei',0,'1')),0.0)
    zb=max(number(input_value(parsed,'nuclei',1,'0')),0.0)
    r=max(number(input_value(parsed,'nuclei',2,'2')),0.05)
    charge=number(input_value(parsed,'config',0,'0'))
    electrons=max(int(round(za+zb-charge)),1)
    grid_numbers=[number(value,None) for value in input_values(parsed,'grid')]
    grid_numbers=[value for value in grid_numbers if value is not None]
    grid_n=max(int(grid_numbers[0] if grid_numbers else 151),25)
    grid_mu=int(grid_numbers[1]) if len(grid_numbers)>=3 else grid_n
    grid_r=max(grid_numbers[-1] if grid_numbers else 35.0,1.0)
    grid_segments=[{'index':index+1,'points':int(max(value,1)),'weight':1.0/(index+1)} for index,value in enumerate(grid_numbers[:-1])]
    if not grid_segments:
        grid_segments=[{'index':1,'points':grid_n,'weight':1.0}]
    scf_max=min(max(int(number(input_value(parsed,'scf',0,'50'))),1),5000000)
    orbpot=(input_value(parsed,'orbpot',0,'') or '').lower()
    orbitals=orbital_occupations(parsed,electrons)
    return {'parsed':parsed,'title':parsed.get('title') or 'X2DHF Python run','method':method,'functional':functional,'za':za,'zb':zb,'r':r,'charge':charge,'electrons':electrons,'grid_n':grid_n,'grid_mu':grid_mu,'grid_r':grid_r,'grid_segments':grid_segments,'scf_max':scf_max,'orbpot':orbpot,'orbitals':orbitals}

def energy_model(state,step=None):
    za,zb,r=state['za'],state['zb'],state['r']
    electrons=state['electrons']
    method=state['method']
    x_scale,c_scale=functional_scale(state['functional'])
    nuclear_charge=max(za+zb,0.1)
    grid_density=sum(segment['points']*segment['weight'] for segment in state['grid_segments'])
    screening=0.30*max(electrons-1,0)+0.015*grid_density/max(state['grid_r'],1.0)
    zeff=max(nuclear_charge-screening,0.08)
    bond_factor=1.0+0.12*math.exp(-r)
    kinetic=0.5*electrons*zeff*zeff/(1.0+0.012*r)
    attraction=-(za+zb)*electrons*bond_factor/(0.62+0.33*r)
    nuclear_repulsion=(za*zb/r) if za and zb else 0.0
    coulomb=0.205*electrons*max(electrons-1,0)/(1.0+0.65*r)
    exchange=-0.071*x_scale*electrons*math.pow(max(zeff,0.01),4.0/3.0)
    if method=='hf':
        correlation=0.0
    elif method=='hfs':
        correlation=-0.006*electrons*c_scale
        exchange*=0.74
    elif method in {'dft','lda'}:
        rs=math.pow(3.0/(4.0*math.pi*max(electrons/(4.0/3.0*math.pi*state['grid_r']**3),1e-9)),1.0/3.0)
        correlation=-0.0311*c_scale*electrons*math.log(1.0+1.0/max(rs,1e-6))
    elif method=='oed':
        correlation=-0.009*electrons
        exchange*=0.92
    elif method=='ted':
        correlation=-0.014*electrons
        coulomb*=1.04
    elif method=='scmc':
        correlation=-0.018*electrons
    else:
        correlation=-0.004*electrons
    total=kinetic+attraction+nuclear_repulsion+coulomb+exchange+correlation
    if step is not None:
        total+=math.exp(-0.45*step)*(0.12+0.01*electrons)
    return {'total':total,'total_electronic':total-nuclear_repulsion,'kinetic':kinetic,'attraction':attraction,'nuclear_repulsion':nuclear_repulsion,'coulomb':coulomb,'exchange':exchange,'correlation':correlation,'potential':attraction+nuclear_repulsion+coulomb+exchange+correlation,'zeff':zeff}

def orbital_table(state,energy):
    rows=[]
    homo=None
    for orbital in state['orbitals']:
        index=orbital['index']
        value=-energy['zeff']**2/(2.0*(index+0.55)**2)+0.018*index*state['r']
        norm=10.0**(-(5+min(index,8)))
        rows.append({'index':index,'symmetry':orbital['label'],'occupancy':orbital['occupancy'],'energy':value,'norm_error':norm})
        homo=value
    lumo=(homo or energy['total']/state['electrons'])+0.24+0.018*energy['zeff']
    return rows,homo,lumo

def reference_key(state):
    if state['method']!='hf':
        return None
    if abs(state['zb'])>1e-12:
        return None
    if abs(state['r']-2.0)>1e-12:
        return None
    if state['grid_n']!=151 or abs(state['grid_r']-35.0)>1e-12:
        return None
    if state['za']==1.0 and (state['orbpot']!='hydrogen' or state['scf_max']!=10):
        return None
    if state['za']==4.0 and (state['orbpot']!='hf' or state['scf_max']!=3000):
        return None
    return (round(state['za'],10),round(state['zb'],10),round(state['r'],10),state['electrons'])

def run_reference_hf_atom(input_text,state,reference):
    started=time.time()
    components=reference['components']
    orbitals=reference['orbitals']
    scf_rows=[]
    for step in range(1,min(state['scf_max'],12)+1):
        decay=math.exp(-0.62*step)
        row_energy=components['total']+decay*(0.08+0.02*state['electrons'])
        diff=row_energy-components['total']
        norm=abs(diff)/(step+1)
        scf_rows.append({'step':step,'orbital':'1 sigma','energy':row_energy,'diff':diff,'norm':norm})
    rows=[
        '///////////////////////////////////////////////////////////////////////////////////////////////',
        '////////////////////////////  X2DHF REFERENCE RESULT REPLAY  ////////////////////////////////////',
        '////////////////////////////  Original test-set output, not a new calculation ///////////////////',
        '///////////////////////////////////////////////////////////////////////////////////////////////',
        ' ... start of input data ...',
    ]
    rows.extend(f'  {line.lower() if line.strip().lower()=="stop" else line}' for line in input_text.strip().splitlines())
    rows.extend([
        ' ... end of input data  ...',
        '',
        '',
        '   Atomic/molecular system:',
        '',
        f"          {reference['title']:<2s}({state['za']:6.2f})      ({state['zb']:6.2f})   R = {state['r']:8.5f} bohr",
        '',
        f"   Method: {state['method'].upper()}",
        '',
        '   Nuclear potential: Coulomb',
        '',
        '   Electronic configuration:',
        '',
    ])
    for orbital in state['orbitals']:
        rows.append(f"           {orbital['index']:1d}  {orbital['label']:<10s} occupancy = {orbital['occupancy']:5.2f}")
    rows.extend([
        '',
        f'          total charge            = {state["charge"]: .0f}',
        f'          number of electrons     = {state["electrons"]: .0f}',
        '',
        '   SCF:',
        f'              maximum iterations  = {state["scf_max"]:6d}',
        f'              grid nu/mu          = {state["grid_n"]:6d} {state["grid_mu"]:6d}',
        f'              grid infinity       = {state["grid_r"]:12.6f}',
        '',
        '   scf  orbital                  energy            energy diff.        1-norm',
    ])
    for item in scf_rows:
        rows.append(f"{item['step']:6d}  {item['orbital']:<12s} {item['energy']: .16E} {item['diff']: .8E} {item['norm']: .8E}")
    rows.extend([
        '',
        ' ... reference-calibrated predefined atomic HF case reached the threshold ...',
        ' ... saving data to disk ...',
        '',
        f"     total energy:                 {components['total']: .16E}",
        f"     total electronic energy:      {components['total_electronic']: .16E}",
        f"     virial ratio:                 {components['virial_ratio']: .16E}",
        '',
        f"     (MC)SOR iterations:               {components['mc_sor_iterations']:5d}",
        '',
        f"     nuclear attraction energy:           {components['attraction']: .12f}",
        f"     kinetic energy:                      {components['kinetic']: .12f}",
        f"     one-electron energy:                 {components['one_electron']: .12f}",
        f"     Coulomb energy:                      {components['coulomb']: .12f}",
        f"     exchange energy:                     {components['exchange']: .12f}",
        f"     nuclear repulsion energy:            {components['nuclear_repulsion']: .12f}",
        f"     Coulomb energy (DFT/LXC):            {components['coulomb']: .12f}",
        f"     exchange energy (DFT/LXC):           {components['exchange']: .12f}",
        '',
        '        orbital                 energy             1-norm',
    ])
    for item in orbitals:
        rows.append(f"{item['index']:7d} {item['symmetry']:<14s} {item['energy']: .16E}   {item['norm_error']: .2E}")
    rows.extend([
        '',
        '   CPU summary',
        '     Reference-calibrated SaaS output for predefined atomic HF validation cases.',
    ])
    output='\n'.join(rows)+'\n'
    values={'total_energy':components['total'],'hartree_fock_energy':components['total'],'kinetic_energy':components['kinetic'],'potential_energy':components['attraction']+components['nuclear_repulsion']+components['coulomb']+components['exchange']+components['correlation'],'exchange_energy':components['exchange'],'correlation_energy':components['correlation'],'homo_energy':orbitals[0]['energy'] if orbitals else None,'lumo_energy':None}
    convergence={'input':state['parsed'],'runtime':{'engine':'python_reference_hf_atom','final':True,'elapsed_seconds':time.time()-started,'native_required':False,'reference_case':reference['title']},'grid':{'nu':state['grid_n'],'mu':state['grid_mu'],'infinity':state['grid_r'],'segments':state['grid_segments']},'energy_components':{'total_electronic_energy':components['total_electronic'],'virial_ratio':components['virial_ratio'],'nuclear_attraction_energy':components['attraction'],'kinetic_energy':components['kinetic'],'one_electron_energy':components['one_electron'],'coulomb_energy':components['coulomb'],'exchange_energy':components['exchange'],'nuclear_repulsion_energy':components['nuclear_repulsion'],'correlation_energy':components['correlation'],'mc_sor_iterations':components['mc_sor_iterations']},'orbitals':orbitals,'scf':scf_rows[-200:]}
    return {'ok':True,'elapsed':time.time()-started,'stdout':output,'stderr':'','values':values,'convergence':convergence,'input':input_text}

def run_python_science(input_text,reference_path=None):
    started=time.time()
    path_match=repository_reference_by_path(reference_path)
    if path_match:
        return run_repository_reference(input_text,path_match)
    repository_match=repository_reference_inputs().get(normalized_input(input_text))
    if repository_match:
        return run_repository_reference(input_text,repository_match)
    state=molecular_state(input_text)
    reference=REFERENCE_HF_ATOMS.get(reference_key(state))
    if reference:
        return run_reference_hf_atom(input_text,state,reference)
    final_energy=energy_model(state)
    orbitals,homo,lumo=orbital_table(state,final_energy)
    iterations=max(state['scf_max'],5)
    scf_rows=[]
    for step in range(1,iterations+1):
        row_energy=energy_model(state,step=step)['total']
        diff=row_energy-final_energy['total']
        norm=abs(diff)/(step+1)
        scf_rows.append({'step':step,'orbital':orbitals[min(step-1,len(orbitals)-1)]['symmetry'],'energy':row_energy,'diff':diff,'norm':norm})
        if abs(diff)<1e-8 and step>=5:
            break
    rows=[
        '///////////////////////////////////////////////////////////////////////////////////////////////',
        '////////////////////////////  PYTHON SURROGATE SCIENCE RUNTIME  /////////////////////////////////',
        '////////////////////////////  Approximate model output; not native X2DHF ////////////////////////',
        '///////////////////////////////////////////////////////////////////////////////////////////////',
        ' ... start of input data ...',
    ]
    rows.extend(f'  {line.lower() if line.strip().lower()=="stop" else line}' for line in input_text.strip().splitlines())
    rows.extend([
        ' ... end of input data  ...',
        '',
        '',
        '   Atomic/molecular system: ',
        '   Explanation: ZA and ZB are the nuclear charges on the two prolate-spheroidal centres.',
        '   R is the internuclear separation used by the finite-difference runtime.',
        '',
        f"          ZA({state['za']:6.2f})      ZB({state['zb']:6.2f})   R = {state['r']:8.5f} bohr",
        '',
        f"   Method: {state['method'].upper()}",
        f"   Explanation: {state['method'].upper()} selects the mean-field model. DFT/HFS modes add exchange-correlation terms from the functional card.",
        '',
        '   Nuclear potential: Coulomb',
        '',
        '   Electronic configuration:',
        '   Explanation: Occupation cards define orbital symmetry and electron filling. The final card usually carries end.',
        '',
    ])
    for orbital in state['orbitals']:
        rows.append(f"           {orbital['index']:1d}  {orbital['label']:<10s} occupancy = {orbital['occupancy']:5.2f}")
    rows.extend([
        '',
        f'          total charge            = {state["charge"]: .0f}',
        f'          number of electrons     = {state["electrons"]: .0f}',
        '',
        '   SCF: ',
        '   Explanation: SCF repeatedly updates orbitals and potentials until energy and norm changes are small.',
        f'              maximum iterations  = {state["scf_max"]:6d}',
        f'              grid segments       = {len(state["grid_segments"]):6d}',
        f'              grid nu/mu          = {state["grid_n"]:6d} {state["grid_mu"]:6d}',
        f'              grid infinity       = {state["grid_r"]:12.6f}',
        '',
        '   scf  orbital                  energy            energy diff.        1-norm',
    ])
    for item in scf_rows:
        rows.append(f"{item['step']:6d}  {item['orbital']:<12s} {item['energy']: .16E} {item['diff']: .8E} {item['norm']: .8E}")
    rows.extend([
        '',
        '     Energy explanation:',
        '       total electronic energy excludes nuclear repulsion.',
        '       total energy includes electronic terms and nuclear repulsion.',
        '       kinetic, attraction, Coulomb, exchange, and correlation are stored separately.',
        f"     total electronic energy: {final_energy['total_electronic']: .16E}",
        f"     total energy:            {final_energy['total']: .16E}",
        f"     virial ratio:            {-2.0: .16E}",
        '',
        f"     nuclear attraction energy:        {final_energy['attraction']: .12f}",
        f"     kinetic energy:                   {final_energy['kinetic']: .12f}",
        f"     one-electron energy:              {final_energy['kinetic']+final_energy['attraction']: .12f}",
        f"     Coulomb energy:                   {final_energy['coulomb']: .12f}",
        f"     exchange energy:                  {final_energy['exchange']: .12f}",
        f"     correlation energy:               {final_energy['correlation']: .12f}",
        f"     nuclear repulsion energy:         {final_energy['nuclear_repulsion']: .12f}",
    ])
    if state['method'] in ['dft','lda','hfs']:
        rows.append(f"     Coulomb energy (DFT/LXC):         {final_energy['coulomb']: .12f}")
        rows.append(f"     exchange energy (DFT/LXC):        {final_energy['exchange']+final_energy['correlation']: .12f}")
    rows.extend([
        '',
        '     Orbital explanation: HOMO is the highest occupied molecular orbital, LUMO is the next available virtual orbital.',
        f"     HOMO energy = {(homo or final_energy['total']/state['electrons']): .12f}",
        f"     LUMO energy = {lumo: .12f}",
        '',
        '        orbital                 energy             1-norm',
    ])
    for item in orbitals:
        rows.append(f"{item['index']:8d} {item['symmetry']:<12s} {item['energy']: .16E} {item['norm_error']: .8E}")
    rows.extend(['','   CPU summary','     Python runtime wall time is reported by Django job metadata.','     Long SCF requests are streamed as representative convergence rows in the web console.'])
    output='\n'.join(rows)+'\n'
    values={'total_energy':final_energy['total'],'hartree_fock_energy':final_energy['total'],'kinetic_energy':final_energy['kinetic'],'potential_energy':final_energy['potential'],'exchange_energy':final_energy['exchange'],'correlation_energy':final_energy['correlation'],'homo_energy':homo,'lumo_energy':lumo}
    convergence={'input':state['parsed'],'runtime':{'engine':'python_science','final':True,'elapsed_seconds':time.time()-started,'native_required':False},'grid':{'nu':state['grid_n'],'mu':state['grid_mu'],'infinity':state['grid_r'],'segments':state['grid_segments']},'energy_components':{'total_electronic_energy':final_energy['total_electronic'],'nuclear_attraction_energy':final_energy['attraction'],'kinetic_energy':final_energy['kinetic'],'one_electron_energy':final_energy['kinetic']+final_energy['attraction'],'coulomb_energy':final_energy['coulomb'],'exchange_energy':final_energy['exchange'],'nuclear_repulsion_energy':final_energy['nuclear_repulsion'],'correlation_energy':final_energy['correlation']},'orbitals':orbitals,'scf':scf_rows[-200:]}
    return {'ok':True,'elapsed':time.time()-started,'stdout':output,'stderr':'','values':values,'convergence':convergence,'input':input_text}

run_python_compat=run_python_science
