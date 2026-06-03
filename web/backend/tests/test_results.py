import pytest
from computations.models import Computation,MolecularSystem
from results.models import ComputationResult


@pytest.mark.django_db
def test_download_raw_returns_saved_output_log(api_client,test_user):
    system=MolecularSystem.objects.create(name='H',molecule_formula='H',geometry_type='atom',user=test_user)
    computation=Computation.objects.create(user=test_user,molecular_system=system,title='H sample',theory='hf',spin_multiplicity=1,num_electrons=1)
    result=ComputationResult.objects.create(user=test_user,computation=computation,output_log='total energy: -0.5\n')
    api_client.force_authenticate(user=test_user)

    response=api_client.get(f'/api/results/results/{result.id}/download_raw/')

    assert response.status_code==200
    assert response['Content-Type'].startswith('text/plain')
    assert response['Content-Disposition']==f'attachment; filename="H_sample_{result.id}.lst"'
    assert response.content==b'total energy: -0.5\n'
