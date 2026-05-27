from rest_framework import viewsets,status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny,IsAuthenticated
from django.contrib.auth.models import User
from django.db.models import Count,Sum
from django.db.models.functions import TruncDate
from computations.models import Computation,MolecularSystem
from results.models import ComputationResult
from billing.models import Invoice,Payment
from users.models import APIAuditLog
from .models import TheoryPost,RuntimeControlPreset
from rest_framework import serializers
from django.utils import timezone

from django.core.mail import send_mail
from django.conf import settings
from django.http import FileResponse,Http404

class TheoryPostSerializer(serializers.ModelSerializer):
    author_email=serializers.EmailField(source='author.email',read_only=True)
    class Meta:
        model=TheoryPost
        fields=['id','title','slug','category','summary','body','status','seo_title','seo_description','author_email','created_at','updated_at','published_at']
        read_only_fields=['id','slug','author_email','created_at','updated_at','published_at']

class RuntimeControlPresetSerializer(serializers.ModelSerializer):
    created_by_email=serializers.EmailField(source='created_by.email',read_only=True)
    class Meta:
        model=RuntimeControlPreset
        fields=['id','name','slug','theory','grid_spec','orbpot','scf_iterations','scf_orbital','scf_potential','advanced_cards','explanation','status','created_by_email','created_at','updated_at']
        read_only_fields=['id','slug','created_by_email','created_at','updated_at']

class StaffWriteMixin:
    permission_classes=[IsAuthenticated]
    def check_staff(self,request):
        if not request.user.is_staff:
            return Response({'error':'Admin access required'},status=status.HTTP_403_FORBIDDEN)
        return None
    def create(self,request,*args,**kwargs):
        blocked=self.check_staff(request)
        if blocked:
            return blocked
        return super().create(request,*args,**kwargs)
    def update(self,request,*args,**kwargs):
        blocked=self.check_staff(request)
        if blocked:
            return blocked
        return super().update(request,*args,**kwargs)
    def partial_update(self,request,*args,**kwargs):
        blocked=self.check_staff(request)
        if blocked:
            return blocked
        return super().partial_update(request,*args,**kwargs)
    def destroy(self,request,*args,**kwargs):
        blocked=self.check_staff(request)
        if blocked:
            return blocked
        return super().destroy(request,*args,**kwargs)

class TheoryPostViewSet(StaffWriteMixin,viewsets.ModelViewSet):
    serializer_class=TheoryPostSerializer
    queryset=TheoryPost.objects.all()
    def get_queryset(self):
        queryset=TheoryPost.objects.all()
        if not self.request.user.is_staff:
            queryset=queryset.filter(status='published')
        return queryset
    def perform_create(self,serializer):
        published_at=timezone.now() if serializer.validated_data.get('status')=='published' else None
        serializer.save(author=self.request.user,published_at=published_at)
    def perform_update(self,serializer):
        instance=self.get_object()
        status_value=serializer.validated_data.get('status',instance.status)
        published_at=instance.published_at
        if status_value=='published' and not published_at:
            published_at=timezone.now()
        serializer.save(published_at=published_at)

class RuntimeControlPresetViewSet(StaffWriteMixin,viewsets.ModelViewSet):
    serializer_class=RuntimeControlPresetSerializer
    queryset=RuntimeControlPreset.objects.all()
    def get_queryset(self):
        queryset=RuntimeControlPreset.objects.all()
        if not self.request.user.is_staff:
            queryset=queryset.filter(status='active')
        return queryset
    def perform_create(self,serializer):
        serializer.save(created_by=self.request.user)
class HealthViewSet(viewsets.ViewSet):
    permission_classes=[AllowAny]
    @action(detail=False,methods=['get'])
    def status(self,request):
        return Response({'status':'healthy','version':'1.0.0'})
class PublicAuthViewSet(viewsets.ViewSet):
    permission_classes=[AllowAny]
    @action(detail=False,methods=['post'])
    def forgot_password(self,request):
        email=str(request.data.get('email','')).strip()
        if '@' not in email or '.' not in email.split('@')[-1]:
            return Response({'email':'Enter a valid email address.'},status=status.HTTP_400_BAD_REQUEST)
        return Response({'message':'If this email exists, a reset link will be sent. In local runserver mode, contact the admin or reset from Django admin.'})

class ContactViewSet(viewsets.ViewSet):
    permission_classes=[AllowAny]
    @action(detail=False,methods=['post'])
    def submit(self,request):
        email=request.data.get('email')
        message=request.data.get('message')
        if not email or not message:
            return Response({'error':'Email and message required'},status=status.HTTP_400_BAD_REQUEST)
        try:
            send_mail('Contact Form Submission',message,email,[settings.ADMIN_EMAIL or 'admin@x2dhf.com'],fail_silently=False)
            return Response({'message':'Message sent'},status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error':str(e)},status=status.HTTP_400_BAD_REQUEST)
class DocumentationViewSet(viewsets.ViewSet):
    permission_classes=[AllowAny]
    @action(detail=False,methods=['get'])
    def guides(self,request):
        return Response({'guides':['Getting Started','API Reference','Computation Guide','Visualization Guide']})
    @action(detail=False,methods=['get'])
    def faq(self,request):
        return Response({'faq':[{'q':'What is X2DHF?','a':'X2DHF is a quantum chemistry computational software for solving Hartree-Fock and DFT equations.'},{'q':'What systems can be studied?','a':'Diatomic molecules, atoms, and linear systems.'},]})
    @action(detail=False,methods=['get'],url_path='users-guide.pdf')
    def users_guide(self,request):
        path=settings.REPO_ROOT/'docs'/'users-guide.pdf'
        if not path.exists():
            raise Http404()
        return FileResponse(path.open('rb'),content_type='application/pdf',filename='x2dhf-users-guide.pdf')

class AnalyticsViewSet(viewsets.ViewSet):
    permission_classes=[IsAuthenticated]

    @action(detail=False,methods=['get'])
    def user(self,request):
        jobs=Computation.objects.filter(user=request.user)
        return Response({'systems':MolecularSystem.objects.filter(user=request.user).count(),'computations':jobs.count(),'results':ComputationResult.objects.filter(user=request.user).count(),'completed':jobs.filter(status='completed').count(),'failed':jobs.filter(status='failed').count(),'running':jobs.filter(status='running').count(),'cpu_time_seconds':jobs.aggregate(value=Sum('cpu_time_seconds'))['value'] or 0,'by_theory':list(jobs.values('theory').annotate(count=Count('id')).order_by('theory')),'activity':list(jobs.annotate(day=TruncDate('created_at')).values('day').annotate(count=Count('id')).order_by('day')),'recent_operations':list(APIAuditLog.objects.filter(user=request.user).order_by('-timestamp').values('endpoint','method','status_code','timestamp')[:12])})

    @action(detail=False,methods=['get'])
    def admin(self,request):
        if not request.user.is_staff:
            return Response({'error':'Admin access required'},status=status.HTTP_403_FORBIDDEN)
        jobs=Computation.objects.all()
        return Response({'users':User.objects.count(),'active_users':User.objects.filter(is_active=True).count(),'systems':MolecularSystem.objects.count(),'computations':jobs.count(),'results':ComputationResult.objects.count(),'completed':jobs.filter(status='completed').count(),'failed':jobs.filter(status='failed').count(),'running':jobs.filter(status='running').count(),'revenue':Payment.objects.filter(status='completed').aggregate(value=Sum('amount'))['value'] or 0,'open_invoices':Invoice.objects.exclude(status='paid').count(),'operations':APIAuditLog.objects.count(),'by_theory':list(jobs.values('theory').annotate(count=Count('id')).order_by('theory')),'activity':list(jobs.annotate(day=TruncDate('created_at')).values('day').annotate(count=Count('id')).order_by('day')),'recent_operations':list(APIAuditLog.objects.order_by('-timestamp').values('user__email','endpoint','method','status_code','timestamp')[:20])})
