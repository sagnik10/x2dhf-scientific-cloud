from rest_framework import serializers
from .models import ComputationResult,ResultVisualization,Export
from computations.serializers import ComputationDetailSerializer
class ResultVisualizationSerializer(serializers.ModelSerializer):
    class Meta:
        model=ResultVisualization
        fields=['id','title','plot_type','plot_data','plot_image','created_at']
        read_only_fields=['id','created_at']
class ComputationResultSerializer(serializers.ModelSerializer):
    computation=ComputationDetailSerializer(read_only=True)
    visualizations=ResultVisualizationSerializer(many=True,read_only=True)
    class Meta:
        model=ComputationResult
        fields=['id','computation','total_energy','hartree_fock_energy','kinetic_energy','potential_energy','exchange_energy','correlation_energy','homo_energy','lumo_energy','dipole_moment','quadrupole_moment','polarizability','convergence_info','result_file','output_log','visualizations','created_at']
        read_only_fields=['id','computation','created_at']
class ExportSerializer(serializers.ModelSerializer):
    class Meta:
        model=Export
        fields=['id','result','format','file','created_at']
        read_only_fields=['id','user','created_at']
