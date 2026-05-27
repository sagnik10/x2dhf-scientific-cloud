from rest_framework import viewsets,status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied,ValidationError
from django.db.models import Avg,Count,Sum
from django.db.models.functions import TruncDate
from django.conf import settings
import os
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter,OrderingFilter
from django.utils import timezone
from .models import MolecularSystem,Computation,ComputationParameter
from .serializers import MolecularSystemSerializer,ComputationListSerializer,ComputationDetailSerializer,ComputationCreateSerializer
from .tasks import run_computation_task
from .science import parse_x2dhf_input,science_metadata
from .services import native_runtime_status,native_build_status,start_native_build
from results.models import ComputationResult
class MolecularSystemViewSet(viewsets.ModelViewSet):
    serializer_class=MolecularSystemSerializer
    permission_classes=[IsAuthenticated]
    filter_backends=[DjangoFilterBackend,SearchFilter,OrderingFilter]
    filterset_fields=['geometry_type','symmetry']
    search_fields=['name','molecule_formula']
    ordering_fields=['created_at','name']
    ordering=['-created_at']
    def get_queryset(self):
        return MolecularSystem.objects.filter(user=self.request.user)
    def perform_create(self,serializer):
        serializer.save(user=self.request.user)
    def perform_destroy(self,instance):
        if instance.computations.exists():
            raise ValidationError('Cannot delete system with existing computations')
        instance.delete()
class ComputationViewSet(viewsets.ModelViewSet):
    permission_classes=[IsAuthenticated]
    filter_backends=[DjangoFilterBackend,SearchFilter,OrderingFilter]
    filterset_fields=['status','theory','molecular_system']
    search_fields=['title','description']
    ordering_fields=['created_at','status']
    ordering=['-created_at']
    def get_queryset(self):
        return Computation.objects.filter(user=self.request.user)
    def get_serializer_class(self):
        if self.action=='create':
            return ComputationCreateSerializer
        elif self.action=='retrieve':
            return ComputationDetailSerializer
        return ComputationListSerializer
    def perform_create(self,serializer):
        molecular_system=serializer.validated_data.get('molecular_system')
        parameters=serializer.validated_data.get('parameters',[])
        raw_input=next((item.get('value') for item in parameters if item.get('key')=='x2dhf_input'),None)
        if molecular_system and molecular_system.user!=self.request.user:
            raise PermissionDenied('Cannot use other users molecular systems')
        if not molecular_system:
            parsed=parse_x2dhf_input(raw_input or '')
            nuclei=next((card for card in parsed['cards'] if card['label']=='nuclei'),None)
            values=nuclei['values'] if nuclei else ['0','0','0']
            formula=f"ZA{values[0]}_ZB{values[1]}" if len(values)>=2 else parsed['title']
            molecular_system=MolecularSystem.objects.create(user=self.request.user,name=parsed['title'],description='Created from native X2DHF input',molecule_formula=formula,geometry_type='diatomic',symmetry='C_inf_v')
        if settings.AUTO_START_COMPUTATIONS and not getattr(settings,'PYTHON_SCIENCE_RUNTIME',True) and not os.environ.get('PYTEST_CURRENT_TEST') and serializer.validated_data.get('theory')!='qe':
            native=native_runtime_status()
            if not native.get('ready'):
                raise ValidationError({'runtime':native.get('message'),'wsl':native.get('wsl'),'build_commands':native.get('build_commands')})
        serializer.validated_data.pop('parameters',None)
        computation=serializer.save(user=self.request.user,status='pending',molecular_system=molecular_system)
        for param in parameters:
            ComputationParameter.objects.create(computation=computation,key=param['key'],value=param['value'])
        if settings.AUTO_START_COMPUTATIONS and not os.environ.get('PYTEST_CURRENT_TEST'):
            run_computation_task.delay(computation.id)
    @action(detail=True,methods=['post'])
    def cancel(self,request,pk=None):
        computation=self.get_object()
        if computation.status not in ['pending','running']:
            return Response({'error':'Cannot cancel completed computation'},status=status.HTTP_400_BAD_REQUEST)
        computation.status='cancelled'
        computation.completed_at=timezone.now()
        computation.save()
        return Response({'message':'Computation cancelled'},status=status.HTTP_200_OK)
    @action(detail=True,methods=['post'])
    def retry(self,request,pk=None):
        computation=self.get_object()
        if computation.status!='failed':
            return Response({'error':'Only failed computations can be retried'},status=status.HTTP_400_BAD_REQUEST)
        computation.status='pending'
        computation.error_message=''
        computation.save()
        run_computation_task.delay(computation.id)
        return Response({'message':'Computation retry started'},status=status.HTTP_200_OK)
    @action(detail=True,methods=['get'])
    def runtime_output(self,request,pk=None):
        computation=self.get_object()
        result=ComputationResult.objects.filter(computation=computation,user=request.user).first()
        return Response({'id':computation.id,'status':computation.status,'error_message':computation.error_message,'output_log':result.output_log if result else '','convergence_info':result.convergence_info if result else {},'updated_at':result.created_at if result else computation.updated_at})
    @action(detail=False,methods=['get'])
    def statistics(self,request):
        computations=self.get_queryset()
        stats={'total':computations.count(),'completed':computations.filter(status='completed').count(),'failed':computations.filter(status='failed').count(),'running':computations.filter(status='running').count(),'pending':computations.filter(status='pending').count(),'cpu_time_seconds':computations.aggregate(value=Sum('cpu_time_seconds'))['value'] or 0,'average_cpu_time_seconds':computations.aggregate(value=Avg('cpu_time_seconds'))['value'] or 0,'by_theory':list(computations.values('theory').annotate(count=Count('id')).order_by('theory')),'timeline':list(computations.annotate(day=TruncDate('created_at')).values('day').annotate(count=Count('id')).order_by('day'))}
        return Response(stats)

    @action(detail=False,methods=['get'])
    def science(self,request):
        return Response(science_metadata())

    @action(detail=False,methods=['get'])
    def native_status(self,request):
        return Response(native_runtime_status())

    @action(detail=False,methods=['get','post'])
    def native_build(self,request):
        if request.method=='GET':
            return Response(native_build_status())
        mode=request.data.get('mode','basic')
        try:
            return Response(start_native_build(mode))
        except Exception as exc:
            messages=getattr(exc,'messages',None)
            return Response({'started':False,'error':'\n'.join(messages) if messages else str(exc),**native_build_status()},status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False,methods=['post'])
    def parse_input(self,request):
        return Response(parse_x2dhf_input(request.data.get('input','')))
