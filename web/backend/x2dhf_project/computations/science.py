import re
from pathlib import Path
from django.conf import settings
from .test_sets import list_test_cases

CARD_HELP={
    'title':{'meaning':'Case title written into output and data files.','format':'title text'},
    'method':{'meaning':'Calculation type: HF, DFT, HFS, OED, TED, or SCMC.','format':'method hf|dft|hfs|oed|ted|scmc'},
    'dft':{'meaning':'DFT exchange-correlation functional label used by native X2DHF Libxc builds or preserved in surrogate mode. Examples include xc_lda_x, xc_gga_x_b88, xc_gga_c_lyp, lda, b88, lyp, vwn.','format':'dft functional [functional]'},
    'nuclei':{'meaning':'Nuclear charges of centres A and B and internuclear distance. Add angstrom when R is not in atomic units.','format':'nuclei ZA ZB R [angstrom]'},
    'config':{'meaning':'Total molecular charge followed by orbital occupation cards in inverse energy order. The deepest orbital card must contain end.','format':'config charge'},
    'grid':{'meaning':'Two-dimensional finite-difference grid. N_nu, optional N_mu or extra segment counts, and practical infinity define accuracy and cost.','format':'grid N_nu R_infinity or grid N_nu N_mu R_infinity'},
    'orbpot':{'meaning':'Initial source of orbitals and potentials: hydrogen, hf, lda, ldasap, old, noexch, nodat, gauss, qrhf.','format':'orbpot source [freeze_power]'},
    'lcao':{'meaning':'Hydrogenic LCAO initialization data for orbitals when orbpot hydrogen is used.','format':'lcao followed by one card per orbital'},
    'scf':{'meaning':'SCF and SOR controls used to relax orbitals and Coulomb/exchange potentials.','format':'scf max macro orbital_threshold potential_threshold extra'},
    'conv':{'meaning':'Convergence guard used to stop when improvement stalls.','format':'conv iterations'},
    'stop':{'meaning':'End of input data.','format':'stop'},
    'mmoments':{'meaning':'Requests multipole moments and charge densities after convergence.','format':'mmoments'},
    'multipol':{'meaning':'Controls multipole expansion boundary values for potentials.','format':'multipol ratio [terms]'},
}

EXAMPLES={
    'Hydrogen HF':"""title H
method hf
nuclei 1.0 0.0 2.0
config 0
 1 sigma + end
grid 151 35.0
orbpot hydrogen
lcao
 1.0 1 0 1.0 0.0 1 0 1.0
scf 10 10 12 16 3
stop""",
    'Beryllium HF':"""title Be
method hf
nuclei 4.0 0.0 2.0
config 0
 1 sigma + -
 1 sigma + - end
grid 151 35.0
orbpot hf
scf 3000 10 12 10 3
conv 3000
stop""",
    'Helium LDA DFT':"""title He
method dft
dft xc_lda_x
nuclei 2.0 0.0 2.0
config 0
 1 sigma end
grid 191 65.0
orbpot hf
scf 3000 10 12 18 3
conv 3000
stop""",
    'Helium GGA Exchange DFT':"""title He B88
method dft
dft xc_gga_x_b88
nuclei 2.0 0.0 2.0
config 0
 1 sigma end
grid 191 65.0
orbpot hf
scf 3000 10 12 18 3
conv 3000
stop""",
    'Helium GGA Correlation DFT':"""title He LYP
method dft
dft xc_gga_x_b88 xc_gga_c_lyp
nuclei 2.0 0.0 2.0
config 0
 1 sigma end
grid 191 65.0
orbpot hf
scf 3000 10 12 18 3
conv 3000
stop""",
}

def strip_comment(line):
    return re.split(r'[!#]',line,1)[0].strip()

def parse_x2dhf_input(text):
    if len(text.encode('utf-8'))>200000:
        return {'title':'','method':'','functional':'','cards':[],'missing':['input too large'],'is_valid':False}
    cards=[]
    for number,line in enumerate(text.splitlines(),1):
        clean=strip_comment(line)
        if not clean:
            continue
        parts=clean.split()
        label=parts[0].lower()
        info=CARD_HELP.get(label,{'meaning':'Orbital occupation, LCAO data, or advanced numeric data interpreted by x2dhf.','format':'free numeric/string card'})
        cards.append({'line':number,'label':label,'values':parts[1:],'raw':clean,'meaning':info['meaning'],'format':info['format']})
    labels=[card['label'] for card in cards]
    required=['title','nuclei','config','grid','orbpot','stop']
    missing=[label for label in required if label not in labels]
    method=next((card['values'][0].lower() for card in cards if card['label']=='method' and card['values']),'hf')
    title=' '.join(next((card['values'] for card in cards if card['label']=='title'),[])) or 'X2DHF calculation'
    functional=' '.join(next((card['values'] for card in cards if card['label']=='dft'),[]))
    allowed_methods={'hf','dft','hfs','oed','ted','scmc'}
    if method not in allowed_methods:
        missing.append('valid method')
    if method=='dft' and not functional:
        missing.append('dft functional')
    grid_card=next((card for card in cards if card['label']=='grid'),None)
    if grid_card:
        try:
            grid_numbers=[float(value) for value in grid_card['values']]
            if len(grid_numbers)<2:
                missing.append('grid values')
            if any(value<=0 for value in grid_numbers):
                missing.append('positive grid values')
        except Exception:
            missing.append('numeric grid values')
    scf_card=next((card for card in cards if card['label']=='scf'),None)
    if scf_card:
        try:
            max_iter=int(float(scf_card['values'][0]))
            if max_iter<1 or max_iter>5000000:
                missing.append('scf iterations 1..5000000')
        except Exception:
            missing.append('numeric scf iterations')
    return {'title':title,'method':method,'functional':functional,'cards':cards,'missing':missing,'is_valid':len(missing)==0}

THEORY_GUIDE={
    'hf':{'name':'Hartree-Fock','summary':'Native X2DHF finite-difference Hartree-Fock execution through the web job runner.'},
    'dft':{'name':'Density Functional Theory','summary':'Native X2DHF DFT execution when the Libxc-enabled binary is built; input cards and result parsing stay web-managed.'},
    'hfs':{'name':'Hartree-Fock-Slater','summary':'Native X2DHF-compatible HFS mode wired through the same web computation lifecycle.'},
    'oed':{'name':'Optimized Effective Density','summary':'Native X2DHF-compatible OED mode for density-driven effective potential workflows.'},
    'ted':{'name':'Two-Electron Density','summary':'Native X2DHF-compatible TED mode with saved cards, parsed energies, and runtime output.'},
    'scmc':{'name':'SCMC','summary':'Native X2DHF-compatible SCMC mode wired into the same web computation lifecycle.'},
    'qe':{'name':'Quantum Espresso-style DFT','summary':'Web form can preserve QE-style DFT metadata; primary local execution remains Python unless an external QE binary is configured.'},
}

def science_metadata():
    return {'cards':CARD_HELP,'examples':EXAMPLES,'test_sets':list_test_cases(),'theories':THEORY_GUIDE,'documents':[{'name':'X2DHF User Guide','url':'/api/core/docs/users-guide.pdf/'}]}
