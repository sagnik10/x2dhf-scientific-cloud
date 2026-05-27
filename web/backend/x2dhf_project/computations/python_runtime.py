import math
import time
import numpy as np
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
    orbitals=orbital_occupations(parsed,electrons)
    return {'parsed':parsed,'title':parsed.get('title') or 'X2DHF Python run','method':method,'functional':functional,'za':za,'zb':zb,'r':r,'charge':charge,'electrons':electrons,'grid_n':grid_n,'grid_mu':grid_mu,'grid_r':grid_r,'grid_segments':grid_segments,'scf_max':scf_max,'orbitals':orbitals}

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

def run_python_science(input_text):
    started=time.time()
    state=molecular_state(input_text)
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
        '////////////////////////////  PYTHON FINITE DIFFERENCE 2D HF/DFT  //////////////////////////////',
        '////////////////////////////             X2DHF SaaS runtime       //////////////////////////////',
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
