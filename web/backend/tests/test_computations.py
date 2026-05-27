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
        command_for(computation,Path('input.data'),Path('output.dat'))
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
    assert 'PYTHON FINITE DIFFERENCE 2D HF/DFT' in result['stdout']
    assert result['values']['total_energy'] is not None

def test_python_science_runtime_accepts_fifty_lakh_iterations():
    from computations.python_runtime import run_python_science
    text='title H\nmethod hf\nnuclei 1.0 0.0 2.0\nconfig 0\n 1 sigma + end\ngrid 151 35.0\norbpot hydrogen\nscf 5000000 10 12 16 3\nstop'
    result=run_python_science(text)
    assert result['ok'] is True
    assert 'maximum iterations  = 5000000' in result['stdout']
    assert result['convergence']['runtime']['engine']=='python_science'
