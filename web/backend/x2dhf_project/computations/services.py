import os
import platform
import re
import shutil
import subprocess
import threading
import time
from pathlib import Path
from django.conf import settings
from django.core.exceptions import ValidationError
from .science import parse_x2dhf_input
from .python_runtime import run_python_science

ENERGY_PATTERNS={
    'total_energy':[r'total\s+energy\s*[=:]\s*(-?\d+(?:\.\d+)?(?:[Ee][+-]?\d+)?)',r'!\s+total energy\s*=\s*(-?\d+(?:\.\d+)?)\s+Ry'],
    'hartree_fock_energy':[r'hartree[- ]?fock\s+energy\s*[=:]\s*(-?\d+(?:\.\d+)?(?:[Ee][+-]?\d+)?)'],
    'kinetic_energy':[r'kinetic\s+energy\s*[=:]\s*(-?\d+(?:\.\d+)?(?:[Ee][+-]?\d+)?)'],
    'potential_energy':[r'potential\s+energy\s*[=:]\s*(-?\d+(?:\.\d+)?(?:[Ee][+-]?\d+)?)'],
    'exchange_energy':[r'exchange\s+energy\s*[=:]\s*(-?\d+(?:\.\d+)?(?:[Ee][+-]?\d+)?)'],
    'correlation_energy':[r'correlation\s+energy\s*[=:]\s*(-?\d+(?:\.\d+)?(?:[Ee][+-]?\d+)?)'],
    'homo_energy':[r'homo\s+energy\s*[=:]\s*(-?\d+(?:\.\d+)?(?:[Ee][+-]?\d+)?)'],
    'lumo_energy':[r'lumo\s+energy\s*[=:]\s*(-?\d+(?:\.\d+)?(?:[Ee][+-]?\d+)?)'],
}
COMPONENT_PATTERNS={
    'total_electronic_energy':r'total electronic energy:\s*(-?\d+(?:\.\d+)?(?:[Ee][+-]?\d+)?)',
    'virial_ratio':r'virial ratio:\s*(-?\d+(?:\.\d+)?(?:[Ee][+-]?\d+)?)',
    'nuclear_attraction_energy':r'nuclear attraction energy:\s*(-?\d+(?:\.\d+)?(?:[Ee][+-]?\d+)?)',
    'kinetic_energy':r'kinetic energy:\s*(-?\d+(?:\.\d+)?(?:[Ee][+-]?\d+)?)',
    'one_electron_energy':r'one-electron energy:\s*(-?\d+(?:\.\d+)?(?:[Ee][+-]?\d+)?)',
    'coulomb_energy':r'Coulomb energy:\s*(-?\d+(?:\.\d+)?(?:[Ee][+-]?\d+)?)',
    'exchange_energy':r'exchange energy:\s*(-?\d+(?:\.\d+)?(?:[Ee][+-]?\d+)?)',
    'nuclear_repulsion_energy':r'nuclear repulsion energy:\s*(-?\d+(?:\.\d+)?(?:[Ee][+-]?\d+)?)',
    'dft_coulomb_energy':r'Coulomb energy \(DFT/LXC\):\s*(-?\d+(?:\.\d+)?(?:[Ee][+-]?\d+)?)',
    'dft_exchange_energy':r'exchange energy \(DFT/LXC\):\s*(-?\d+(?:\.\d+)?(?:[Ee][+-]?\d+)?)',
    'mc_sor_iterations':r'\(MC\)SOR iterations:\s*(\d+)',
}
NATIVE_BUILD_STATE={'running':False,'mode':'','exit_code':None,'error':''}

def parameter_map(computation):
    return {item.key:item.value for item in computation.parameters.all()}

def build_x2dhf_input(computation):
    params=parameter_map(computation)
    if params.get('x2dhf_input'):
        return params['x2dhf_input'].strip()+'\n'
    mol=computation.molecular_system
    rows=[
        f"MOLECULE {mol.molecule_formula}",
        f"GEOMETRY {mol.geometry_type}",
        f"SYMMETRY {mol.symmetry}",
        f"GRID {mol.grid_size_x} {mol.grid_size_y}",
        f"SPACING {mol.grid_spacing}",
        f"MAX_RADIUS {mol.max_radius}",
        f"THEORY {computation.theory}",
        f"FUNCTIONAL {computation.functional or 'LDA_X'}",
        f"SPIN {computation.spin_multiplicity}",
        f"ELECTRONS {computation.num_electrons}",
        f"SCF_ITERATIONS {computation.scf_iterations}",
        f"CONVERGENCE {computation.convergence_threshold}",
    ]
    rows.extend(f"{key.upper()} {value}" for key,value in parameter_map(computation).items())
    return '\n'.join(rows)+'\n'

def build_qe_input(computation):
    params=parameter_map(computation)
    prefix=params.get('prefix',f'x2dhf_{computation.id}')
    pseudo=params.get('pseudo','H.pbe-rrkjus.UPF')
    nat=params.get('nat','1')
    ntyp=params.get('ntyp','1')
    ecutwfc=params.get('ecutwfc','40')
    occupations=params.get('occupations','smearing')
    smearing=params.get('smearing','gaussian')
    degauss=params.get('degauss','0.01')
    atoms=params.get('atoms','H 1.0 0.0 0.0 0.0')
    positions=params.get('positions','H 0.0 0.0 0.0')
    cell=params.get('cell','10.0 0.0 0.0\n0.0 10.0 0.0\n0.0 0.0 10.0')
    calculation=params.get('calculation','scf')
    functional=computation.functional or params.get('input_dft','PBE')
    return f"""&CONTROL
 calculation='{calculation}',
 prefix='{prefix}',
 pseudo_dir='{settings.PSEUDO_DIR}',
 outdir='./tmp'
/
&SYSTEM
 ibrav=0,
 nat={nat},
 ntyp={ntyp},
 ecutwfc={ecutwfc},
 occupations='{occupations}',
 smearing='{smearing}',
 degauss={degauss},
 input_dft='{functional}'
/
&ELECTRONS
 conv_thr={computation.convergence_threshold},
 electron_maxstep={computation.scf_iterations}
/
ATOMIC_SPECIES
{atoms} {pseudo}
ATOMIC_POSITIONS angstrom
{positions}
CELL_PARAMETERS angstrom
{cell}
"""

def executable_path(path):
    resolved=Path(path)
    if not resolved.exists():
        found=shutil.which(str(path))
        if found:
            return found
        raise ValidationError(f'Executable not found: {path}')
    return str(resolved)

def windows_to_wsl_path(path):
    resolved=str(Path(path).resolve())
    drive=resolved[0].lower()
    rest=resolved[2:].replace('\\','/')
    return f'/mnt/{drive}{rest}'

def x2dhf_root():
    root=Path(settings.X2DHF_DIRECTORY)
    if root.is_absolute():
        return root
    return Path(getattr(settings,'REPO_ROOT',Path.cwd())).resolve()

def wsl_status():
    if platform.system().lower()!='windows':
        return {'required':False,'available':False,'ready':True,'message':'Native Linux runtime'}
    if not shutil.which('wsl.exe'):
        return {'required':True,'available':False,'ready':False,'message':'WSL is not installed'}
    try:
        result=subprocess.run(['wsl.exe','-l','-q'],capture_output=True,text=True,timeout=10)
        names=[line.strip('\x00 \r\n') for line in (result.stdout or '').splitlines()]
        names=[name for name in names if name and 'Windows Subsystem for Linux has no installed distributions' not in name]
        if result.returncode==0 and names:
            return {'required':True,'available':True,'ready':True,'distributions':names,'message':'WSL distribution available'}
        message=(result.stderr or result.stdout or 'WSL has no installed Linux distribution').replace('\x00','').strip()
        return {'required':True,'available':True,'ready':False,'distributions':[],'message':message}
    except Exception as exc:
        return {'required':True,'available':True,'ready':False,'distributions':[],'message':str(exc)}

def native_source_summary():
    root=x2dhf_root()
    patterns={'fortran':['*.f','*.f90','*.F','*.F90'],'c':['*.c','*.h'],'inputs':['input*.data']}
    summary={}
    for key,globs in patterns.items():
        files=[]
        bases=[root/'src',root/'include'] if key!='inputs' else [root/'test-sets']
        for base in bases:
            for pattern in globs:
                files.extend(base.rglob(pattern) if base.exists() else [])
        summary[key]={'count':len(files),'examples':['/'.join(path.relative_to(root).parts) for path in files[:8]]}
    return summary

def native_runtime_status():
    root=x2dhf_root()
    candidates=['x2dhf','x2dhf-s','x2dhf-s-lxc','x2dhf-lxc','x2dhf-openmp','x2dhf-openmp-lxc','x2dhf-pthread','x2dhf-pthread-lxc','x2dhf-tpool','x2dhf-tpool-lxc']
    binaries=[name for name in candidates if (root/'bin'/name).exists()]
    wrapper=(root/'bin'/'xhf').exists()
    wsl=wsl_status()
    ready=bool(binaries) and (platform.system().lower()!='windows' or wsl.get('ready'))
    return {
        'ready':ready,
        'os':platform.system(),
        'root':str(root),
        'wrapper_present':wrapper,
        'compiled_binaries':binaries,
        'missing_binaries':[] if binaries else candidates,
        'wsl':wsl,
        'build_commands':{
            'install_wsl':'wsl --install -d Ubuntu',
            'install_deps':'apt-get update && apt-get install -y build-essential gfortran cmake make gcc g++ libblas-dev liblapack-dev wget ca-certificates',
            'basic':'./x2dhfctl -b',
            'libxc':'./x2dhfctl -L && ./x2dhfctl -b -l',
            'openmp_libxc':'./x2dhfctl -L && ./x2dhfctl -b -l -o',
            'windows_wsl':'Use the setup buttons below: Install Ubuntu WSL, Install Linux dependencies, then Build Libxc DFT.'
        },
        'sources':native_source_summary(),
        'python_runtime':{
            'ready':bool(getattr(settings,'PYTHON_SCIENCE_RUNTIME',True)),
            'engine':'python_science',
            'primary':not bool(getattr(settings,'USE_NATIVE_X2DHF',False)),
            'message':'Primary Python science runtime is ready for web-based HF and DFT execution.'
        },
        'message':'Native runtime ready' if ready else 'Native runtime is not ready: install a Linux runtime and build the Fortran/C binary into bin/.'
    }

def native_build_log_path():
    root=Path(settings.COMPUTATION_WORKDIR)
    root.mkdir(parents=True,exist_ok=True)
    return root/'native_build.log'

def native_build_command(mode='basic'):
    root=x2dhf_root()
    commands={
        'basic':'./x2dhfctl -b',
        'libxc':'./x2dhfctl -L && ./x2dhfctl -b -l',
        'openmp_libxc':'./x2dhfctl -L && ./x2dhfctl -b -l -o',
    }
    if mode=='install_wsl':
        if platform.system().lower()!='windows':
            raise ValidationError('WSL installation is only needed on Windows.')
        script="Start-Process -FilePath wsl.exe -ArgumentList '--install','-d','Ubuntu' -Verb RunAs -Wait"
        if not shutil.which('wsl.exe'):
            script="Start-Process -FilePath powershell.exe -ArgumentList '-NoProfile','-ExecutionPolicy','Bypass','-Command','Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux -NoRestart; Enable-WindowsOptionalFeature -Online -FeatureName VirtualMachinePlatform -NoRestart; wsl --install -d Ubuntu' -Verb RunAs -Wait"
        return ['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-Command',script]
    if mode=='install_deps':
        packages='build-essential gfortran cmake make gcc g++ libblas-dev liblapack-dev wget ca-certificates'
        script=f'apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y {packages}'
        if platform.system().lower()=='windows':
            status=wsl_status()
            if not status.get('ready'):
                raise ValidationError('Install Ubuntu WSL first, then restart if Windows asks, reopen runserver, and press Install Linux dependencies.')
            return ['wsl.exe','-u','root','bash','-lc',script]
        return ['bash','-lc',f'command -v apt-get >/dev/null && sudo {script} || true']
    script=commands.get(mode,commands['basic'])
    if platform.system().lower()=='windows':
        status=wsl_status()
        if not status.get('ready'):
            raise ValidationError(f"{status.get('message')}. Install Ubuntu with `wsl --install -d Ubuntu`, restart, then press Build again.")
        return ['wsl.exe','bash','-lc',f"cd {windows_to_wsl_path(root)} && {script}"]
    return ['bash','-lc',f"cd {root} && {script}"]

def native_build_status():
    log_path=native_build_log_path()
    log=log_path.read_text(encoding='utf-8',errors='replace')[-12000:] if log_path.exists() else ''
    return {'log':log,'log_path':str(log_path),'build_running':NATIVE_BUILD_STATE['running'],'build_mode':NATIVE_BUILD_STATE['mode'],'build_exit_code':NATIVE_BUILD_STATE['exit_code'],'build_error':NATIVE_BUILD_STATE['error'],**native_runtime_status()}

def start_native_build(mode='basic'):
    if NATIVE_BUILD_STATE['running']:
        return {'started':False,'message':'A native build is already running',**native_build_status()}
    command=native_build_command(mode)
    log_path=native_build_log_path()
    NATIVE_BUILD_STATE.update({'running':True,'mode':mode,'exit_code':None,'error':''})
    log_path.write_text(f"Starting X2DHF native build: {mode}\nCommand: {' '.join(command)}\n\n",encoding='utf-8')
    def worker():
        with log_path.open('a',encoding='utf-8',errors='replace') as log:
            try:
                process=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT,text=True)
                code=process.wait()
                NATIVE_BUILD_STATE.update({'running':False,'exit_code':code,'error':'' if code==0 else f'Build exited with code {code}'})
                log.write(f"\nBuild finished with exit code {code}\n")
            except Exception as exc:
                NATIVE_BUILD_STATE.update({'running':False,'exit_code':None,'error':str(exc)})
                log.write(f"\nBuild failed to start: {exc}\n")
    threading.Thread(target=worker,daemon=True).start()
    return {'started':True,'mode':mode,'command':command,'log_path':str(log_path),**native_build_status()}

def bash_command(script,args):
    script_path=Path(script)
    if platform.system().lower()!='windows':
        return [executable_path(script),*args]
    if shutil.which('wsl.exe'):
        status=wsl_status()
        if not status.get('ready'):
            raise ValidationError(status.get('message') or 'WSL has no installed Linux distribution')
        return ['wsl.exe','bash',windows_to_wsl_path(script_path),*args]
    bash=shutil.which('bash.exe') or shutil.which('bash')
    if bash:
        return [bash,str(script_path),*args]
    raise ValidationError('X2DHF is a Linux/Bash runtime. Install WSL or run this SaaS on Linux, then compile x2dhf-s or x2dhf-lxc in bin.')

def ensure_x2dhf_build():
    root=x2dhf_root()
    wsl=wsl_status()
    if platform.system().lower()=='windows' and not wsl.get('ready'):
        raise ValidationError(f"{wsl.get('message')}. Install a Linux distribution with `wsl --install -d Ubuntu`, then build X2DHF inside WSL.")
    candidates=['x2dhf','x2dhf-s','x2dhf-s-lxc','x2dhf-lxc','x2dhf-openmp','x2dhf-openmp-lxc','x2dhf-pthread','x2dhf-pthread-lxc','x2dhf-tpool','x2dhf-tpool-lxc']
    if any((root/'bin'/name).exists() for name in candidates):
        return
    raise ValidationError(f'Compiled X2DHF binary is missing. Build the Fortran code on Linux/WSL so one of {", ".join(candidates)} exists in {root / "bin"}.')

def native_available():
    root=x2dhf_root()
    candidates=['x2dhf','x2dhf-s','x2dhf-s-lxc','x2dhf-lxc','x2dhf-openmp','x2dhf-openmp-lxc','x2dhf-pthread','x2dhf-pthread-lxc','x2dhf-tpool','x2dhf-tpool-lxc']
    if platform.system().lower()=='windows' and not wsl_status().get('ready'):
        return False
    return any((root/'bin'/name).exists() for name in candidates)

def command_for(computation,input_path,output_path):
    if computation.theory=='qe':
        return [executable_path(settings.QE_BINARY_PATH),'-in',str(input_path)], output_path.open('w')
    ensure_x2dhf_build()
    return bash_command(settings.X2DHF_BINARY_PATH,[input_path.stem,output_path.stem]), subprocess.PIPE

def runtime_env():
    env=os.environ.copy()
    env['X2DHF_DIRECTORY']=windows_to_wsl_path(settings.X2DHF_DIRECTORY) if platform.system().lower()=='windows' and shutil.which('wsl.exe') else settings.X2DHF_DIRECTORY
    if settings.LIBXC_LIBRARY_PATH:
        key='LD_LIBRARY_PATH'
        env[key]=settings.LIBXC_LIBRARY_PATH+os.pathsep+env.get(key,'')
    return env

def parse_results(text):
    data={}
    for key,patterns in ENERGY_PATTERNS.items():
        for pattern in patterns:
            match=re.search(pattern,text,re.IGNORECASE)
            if match:
                data[key]=float(match.group(1))
                break
    components={}
    for key,pattern in COMPONENT_PATTERNS.items():
        match=re.search(pattern,text,re.IGNORECASE)
        if match:
            value=match.group(1)
            components[key]=int(value) if value.isdigit() else float(value)
    orbitals=[]
    orbital_block=re.search(r'orbital\s+energy\s+1-norm(?P<body>.*?)(?:total energy uncertainty|/{20,}|CPU summary)',text,re.IGNORECASE|re.DOTALL)
    if orbital_block:
        for line in orbital_block.group('body').splitlines():
            match=re.search(r'^\s*(\d+)\s+([A-Za-z]+(?:\s+[ug])?)\s+(-?\d+(?:\.\d+)?(?:[Ee][+-]?\d+)?)\s+(\d+(?:\.\d+)?(?:[Ee][+-]?\d+)?)',line)
            if match:
                orbitals.append({'index':int(match.group(1)),'symmetry':match.group(2).strip(),'energy':float(match.group(3)),'norm_error':float(match.group(4))})
    scf_rows=[]
    for match in re.finditer(r'^\s*(\d+)\s+(\d+\s+\w+)\s+(-?\d+(?:\.\d+)?(?:[Ee][+-]?\d+)?)\s+(-?\d+(?:\.\d+)?(?:[Ee][+-]?\d+)?)\s+(\d+(?:\.\d+)?(?:[Ee][+-]?\d+)?)',text,re.IGNORECASE|re.MULTILINE):
        scf_rows.append({'scf':int(match.group(1)),'orbital':match.group(2).strip(),'energy':float(match.group(3)),'energy_diff':float(match.group(4)),'norm':float(match.group(5))})
    return data,{'energy_components':components,'orbitals':orbitals,'scf':scf_rows[-200:]}

def persist_runtime(computation,output_path,input_text,started,final=False):
    from results.models import ComputationResult
    output=output_path.read_text(encoding='utf-8',errors='replace') if output_path.exists() else ''
    values,convergence=parse_results(output)
    convergence['input']=parse_x2dhf_input(input_text)
    convergence['runtime']={'final':final,'elapsed_seconds':time.time()-started}
    ComputationResult.objects.update_or_create(computation=computation,defaults={'user':computation.user,'output_log':output,'convergence_info':convergence,**values})
    return output,values,convergence

def run_engine(computation):
    root=Path(settings.COMPUTATION_WORKDIR)
    root.mkdir(parents=True,exist_ok=True)
    workdir=root/f'job_{computation.id}'
    if workdir.exists():
        shutil.rmtree(workdir)
    workdir.mkdir(parents=True)
    is_qe=computation.theory=='qe'
    input_path=workdir/'input.in' if is_qe else workdir/'input.data'
    output_path=workdir/'output.out' if is_qe else workdir/'output.dat'
    input_path.write_text(build_qe_input(computation) if is_qe else build_x2dhf_input(computation),encoding='utf-8')
    if not is_qe and getattr(settings,'PYTHON_SCIENCE_RUNTIME',True) and (not getattr(settings,'USE_NATIVE_X2DHF',False) or not native_available()):
        return run_python_science(input_path.read_text(encoding='utf-8'))
    started=time.time()
    output_handle=None
    try:
        command,stdout=command_for(computation,input_path,output_path)
        if stdout is not subprocess.PIPE:
            output_handle=stdout
        input_text=input_path.read_text(encoding='utf-8')
        process=subprocess.Popen(command,cwd=workdir,env=runtime_env(),stdout=stdout,stderr=subprocess.PIPE,text=True)
        stderr_parts=[]
        while True:
            if process.poll() is not None:
                break
            if time.time()-started>settings.MAX_COMPUTATION_TIME:
                process.kill()
                raise subprocess.TimeoutExpired(command,settings.MAX_COMPUTATION_TIME)
            persist_runtime(computation,output_path,input_text,started)
            time.sleep(1)
        stderr=process.stderr.read() if process.stderr else ''
        if stderr:
            stderr_parts.append(stderr)
        if output_handle:
            output_handle.close()
        elapsed=time.time()-started
        output,values,convergence=persist_runtime(computation,output_path,input_text,started,final=True)
        if process.returncode!=0:
            return {'ok':False,'elapsed':elapsed,'stdout':output,'stderr':'\n'.join(stderr_parts) or output,'values':values,'convergence':convergence}
        return {'ok':True,'elapsed':elapsed,'stdout':output,'stderr':'\n'.join(stderr_parts),'values':values,'convergence':convergence,'input':input_text}
    finally:
        if output_handle and not output_handle.closed:
            output_handle.close()
