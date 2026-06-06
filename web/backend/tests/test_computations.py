import pytest
from django.contrib.auth.models import User
from computations.models import MolecularSystem,Computation
from computations.services import build_x2dhf_input,command_for,native_runtime_status,run_engine
from django.core.exceptions import ValidationError
from pathlib import Path
@pytest.fixture
def test_user(db):
    return User.objects.create_user(username='testuser',email='test@example.com',password='testpass123')
@pytest.fixture
def test_molecular_system(db,test_user):
    return MolecularSystem.objects.create(name='H2',description='Hydrogen molecule',molecule_formula='H2',geometry_type='diatomic',symmetry='D_inf_h',user=test_user)
@pytest.mark.django_db
def test_create_molecular_system(api_client,test_user):
    api_client.force_authenticate(user=test_user)
    response=api_client.post('/api/computations/systems/',{'name':'H2O','description':'Water molecule','molecule_formula':'H2O','geometry_type':'diatomic','symmetry':'C2v'})
    assert response.status_code==201
@pytest.mark.django_db
def test_create_computation(api_client,test_user,test_molecular_system):
    api_client.force_authenticate(user=test_user)
    response=api_client.post('/api/computations/jobs/',{'molecular_system':test_molecular_system.id,'title':'HF Computation','theory':'hf','spin_multiplicity':1,'num_electrons':2})
    assert response.status_code==201
    assert 'id' in response.data

@pytest.mark.django_db
def test_native_input_is_preserved(test_user,test_molecular_system):
    computation=Computation.objects.create(user=test_user,molecular_system=test_molecular_system,title='Native',theory='hf',spin_multiplicity=1,num_electrons=1)
    computation.parameters.create(key='x2dhf_input',value='title H\nmethod hf\nstop')
    assert build_x2dhf_input(computation)=='title H\nmethod hf\nstop\n'

@pytest.mark.django_db
def test_missing_native_binary_reports_build_problem(settings,test_user,test_molecular_system,tmp_path):
    settings.X2DHF_DIRECTORY=str(tmp_path)
    settings.X2DHF_BINARY_PATH=str(tmp_path/'bin'/'xhf')
    computation=Computation.objects.create(user=test_user,molecular_system=test_molecular_system,title='Native',theory='hf',spin_multiplicity=1,num_electrons=1)
    with pytest.raises(ValidationError) as exc:
        command_for(computation,Path('input.data'),Path('output.lst'),tmp_path)
    assert 'Compiled X2DHF binary is missing' in str(exc.value) or 'WSL has no installed Linux distribution' in str(exc.value)

@pytest.mark.django_db
def test_native_mode_does_not_silently_fallback_to_python(settings,test_user,test_molecular_system,tmp_path):
    settings.X2DHF_DIRECTORY=str(tmp_path)
    settings.X2DHF_BINARY_PATH=str(tmp_path/'bin'/'xhf')
    settings.COMPUTATION_WORKDIR=str(tmp_path/'work')
    settings.PYTHON_SCIENCE_RUNTIME=True
    settings.USE_NATIVE_X2DHF=True
    computation=Computation.objects.create(user=test_user,molecular_system=test_molecular_system,title='Native required',theory='hf',spin_multiplicity=1,num_electrons=1)
    computation.parameters.create(key='x2dhf_input',value='title H\nmethod hf\nnuclei 1.0 0.0 2.0\nconfig 0\n 1 sigma + end\ngrid 151 35.0\norbpot hydrogen\nscf 10 10 12 16 3\nstop')
    with pytest.raises(ValidationError) as exc:
        run_engine(computation)
    assert 'Compiled X2DHF binary is missing' in str(exc.value) or 'WSL has no installed Linux distribution' in str(exc.value)

@pytest.mark.django_db
def test_native_status_endpoint_reports_sources(api_client,test_user):
    api_client.force_authenticate(user=test_user)
    response=api_client.get('/api/computations/jobs/native_status/')
    assert response.status_code==200
    assert 'sources' in response.data
    assert 'fortran' in response.data['sources']

def test_native_runtime_status_shape():
    status=native_runtime_status()
    assert 'ready' in status
    assert 'build_commands' in status
    assert 'install_wsl' in status['build_commands']
    assert 'install_deps' in status['build_commands']
    assert status['python_runtime']['ready'] is True

@pytest.mark.django_db
def test_python_science_runtime_completes_without_native_binary(settings,test_user,test_molecular_system,tmp_path):
    settings.X2DHF_DIRECTORY=str(tmp_path)
    settings.COMPUTATION_WORKDIR=str(tmp_path/'work')
    settings.PYTHON_SCIENCE_RUNTIME=True
    settings.USE_NATIVE_X2DHF=False
    computation=Computation.objects.create(user=test_user,molecular_system=test_molecular_system,title='Python compat',theory='hf',spin_multiplicity=1,num_electrons=1)
    computation.parameters.create(key='x2dhf_input',value='title H\nmethod hf\nnuclei 1.0 0.0 2.0\nconfig 0\n 1 sigma + end\ngrid 151 35.0\norbpot hydrogen\nscf 10 10 12 16 3\nstop')
    result=run_engine(computation)
    assert result['ok'] is True
    assert 'X2DHF REFERENCE RESULT REPLAY' in result['stdout']
    assert 'Original test-set output, not a new calculation' in result['stdout']
    assert 'PYTHON FINITE DIFFERENCE 2D HF/DFT' not in result['stdout']
    assert result['values']['total_energy'] is not None

def test_python_science_runtime_accepts_fifty_lakh_iterations():
    from computations.python_runtime import run_python_science
    text='title H\nmethod hf\nnuclei 1.0 0.0 2.0\nconfig 0\n 1 sigma + end\ngrid 151 35.0\norbpot hydrogen\nscf 5000000 10 12 16 3\nstop'
    result=run_python_science(text)
    assert result['ok'] is True
    assert 'maximum iterations  = 5000000' in result['stdout']
    assert result['convergence']['runtime']['engine']=='python_finite_difference_schrodinger'
    assert 'Sparse-grid numerical Hamiltonian; no Gaussian basis set' in result['stdout']

def test_python_runtime_solves_one_electron_diatomic_with_finite_difference():
    from computations.python_runtime import run_python_science
    text='title H2+ FD\nmethod hf\nnuclei 1.0 1.0 2.0\nconfig 1\n 1 sigma + end\ngrid 27 18.0\norbpot hydrogen\nscf 20 10 12 16 3\nstop'
    result=run_python_science(text)
    assert result['ok'] is True
    assert result['convergence']['runtime']['engine']=='python_finite_difference_schrodinger'
    assert result['convergence']['grid']['dimensions']==3
    assert result['values']['total_energy']<0.0
    assert 'PYTHON SURROGATE SCIENCE RUNTIME' not in result['stdout']

def test_python_runtime_reproduces_predefined_h_reference():
    from computations.python_runtime import run_python_science
    text='title H\nmethod hf\nnuclei 1.0 0.0 2.0\nconfig 0\n 1 sigma + end\ngrid 151 35.0\norbpot hydrogen\nlcao\n 1.0 1 0 1.0 0.0 1 0 1.0\nscf 10 10 12 16 3\nstop'
    result=run_python_science(text)
    assert result['ok'] is True
    assert result['convergence']['runtime']['engine'] in {'repository_reference','python_reference_hf_atom'}
    assert result['values']['total_energy']==pytest.approx(-5.0000000000025846E-01)

def test_python_runtime_reproduces_predefined_be_reference():
    from computations.python_runtime import run_python_science
    text='title Be\nmethod hf\nnuclei 4.0 0.0 2.0\nconfig 0\n 1 sigma + -\n 1 sigma + - end\ngrid 151 35.0\norbpot hf\nscf 3000 10 12 10 3\nconv 3000\nstop'
    result=run_python_science(text)
    assert result['ok'] is True
    assert result['convergence']['runtime']['engine']=='python_reference_hf_atom'
    assert result['values']['total_energy']==pytest.approx(-1.4573023167779406E+01)

def test_repository_predefined_inputs_replay_matching_references(settings):
    from computations.python_runtime import reference_for_input_path,run_python_science
    root=Path(settings.REPO_ROOT)/'test-sets'
    checked=0
    for input_path in sorted(root.glob('*/*/input*.data')):
        reference_path=reference_for_input_path(input_path)
        if not reference_path.exists():
            continue
        result=run_python_science(input_path.read_text(encoding='utf-8',errors='replace'),reference_path='/'.join(reference_path.relative_to(root).parts))
        assert result['ok'] is True
        assert result['convergence']['runtime']['engine']=='repository_reference'
        assert result['stdout']==reference_path.read_text(encoding='utf-8',errors='replace')
        checked+=1
    assert checked>=300

def test_python_surrogate_output_does_not_claim_native_x2dhf():
    from computations.python_runtime import run_python_science
    text='title Unmatched\nmethod hf\nnuclei 1.0 1.0 1.8\nconfig 0\n 1 sigma + - end\ngrid 99 20.0\norbpot hf\nscf 7 10 12 16 3\nstop'
    result=run_python_science(text)
    assert result['ok'] is True
    assert result['convergence']['runtime']['engine']=='python_science'
    assert 'PYTHON SURROGATE SCIENCE RUNTIME' in result['stdout']
    assert 'not native X2DHF' in result['stdout']
    assert 'PYTHON FINITE DIFFERENCE 2D HF/DFT' not in result['stdout']
