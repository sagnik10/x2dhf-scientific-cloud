from rest_framework import serializers
from .models import MolecularSystem,Computation,ComputationParameter
from .science import parse_x2dhf_input
class ComputationParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model=ComputationParameter
        fields=['id','key','value']
class MolecularSystemSerializer(serializers.ModelSerializer):
    class Meta:
        model=MolecularSystem
        fields=['id','name','description','molecule_formula','geometry_type','symmetry','grid_spacing','max_radius','grid_size_x','grid_size_y','user','created_at','updated_at']
        read_only_fields=['id','user','created_at','updated_at']
class ComputationListSerializer(serializers.ModelSerializer):
    class Meta:
        model=Computation
        fields=['id','molecular_system','title','description','theory','engine','status','cpu_time_seconds','created_at','updated_at']
        read_only_fields=['id','status','cpu_time_seconds','created_at','updated_at']
class ComputationDetailSerializer(serializers.ModelSerializer):
    parameters=ComputationParameterSerializer(many=True,read_only=True)
    molecular_system=MolecularSystemSerializer(read_only=True)
    class Meta:
        model=Computation
        fields=['id','molecular_system','title','description','theory','engine','functional','spin_multiplicity','num_electrons','scf_iterations','convergence_threshold','status','task_id','cpu_time_seconds','memory_usage_mb','error_message','parameters','started_at','completed_at','created_at','updated_at']
        read_only_fields=['id','status','task_id','cpu_time_seconds','memory_usage_mb','error_message','started_at','completed_at','created_at','updated_at']
class ComputationCreateSerializer(serializers.ModelSerializer):
    molecular_system=serializers.PrimaryKeyRelatedField(queryset=MolecularSystem.objects.all(),required=False,allow_null=True)
    parameters=serializers.ListField(child=serializers.DictField(),required=False,write_only=True)
    class Meta:
        model=Computation
        fields=['id','molecular_system','title','description','theory','engine','functional','spin_multiplicity','num_electrons','scf_iterations','convergence_threshold','status','created_at','parameters']
        read_only_fields=['id','status','created_at']

    def validate(self,attrs):
        theory=attrs.get('theory','hf')
        parameters=attrs.get('parameters') or []
        raw_input=next((item.get('value') for item in parameters if item.get('key')=='x2dhf_input'),None)
        if raw_input and not parse_x2dhf_input(raw_input)['is_valid']:
            missing=', '.join(parse_x2dhf_input(raw_input)['missing'])
            raise serializers.ValidationError({'x2dhf_input':f'Missing required X2DHF cards: {missing}'})
        if theory=='qe':
            attrs['engine']='quantum_espresso'
        if theory in ['dft','lda'] and not attrs.get('functional'):
            attrs['functional']='LDA_X'
        return attrs
