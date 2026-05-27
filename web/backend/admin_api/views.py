from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.contrib.auth.models import User
from django.db.models import Count,Sum,Avg
from django.utils import timezone
from datetime import timedelta
from typing import Any,cast
from computations.models import Computation
from billing.models import Payment
from results.models import ComputationResult
from computations.tasks import run_computation_task
@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_statistics(request):
    now=timezone.now()
    thirty_days_ago=now-timedelta(days=30)
    comps=Computation.objects.all()
    users=User.objects.all()
    theory_dist=comps.values('theory').annotate(count=Count('id')).order_by('theory')
    return Response({
        'total_computations':comps.count(),
        'completed_computations':comps.filter(status='completed').count(),
        'failed_computations':comps.filter(status='failed').count(),
        'running_computations':comps.filter(status='running').count(),
        'pending_computations':comps.filter(status='pending').count(),
        'active_users':users.filter(last_login__gte=thirty_days_ago).count(),
        'total_users':users.count(),
        'total_cpu_time_hours':(comps.aggregate(total=Sum('cpu_time_seconds'))['total'] or 0)/3600,
        'avg_execution_time_sec':comps.aggregate(avg=Avg('cpu_time_seconds'))['avg'] or 0,
        'theory_distribution':{item['theory']:item['count'] for item in theory_dist},
        'status_distribution':{st[0]:comps.filter(status=st[0]).count() for st in Computation.STATUS_CHOICES},
        'computations_this_month':comps.filter(created_at__gte=thirty_days_ago).count(),
        'new_users_this_month':users.filter(date_joined__gte=thirty_days_ago).count(),
        'total_revenue_usd':sum(float(p.amount) for p in Payment.objects.filter(status='completed',created_at__gte=thirty_days_ago)),
    })
@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_users_list(request):
    users=User.objects.annotate(computation_count=Count('computations')).values('id','username','email','date_joined','last_login','computation_count').order_by('-date_joined')
    return Response(list(users))
@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_computations_detail(request,pk):
    comp=cast(Any,Computation.objects.get(pk=pk))
    result=ComputationResult.objects.filter(computation=comp).first()
    return Response({
        'id':comp.pk,
        'title':comp.title,
        'status':comp.status,
        'theory':comp.theory,
        'user':comp.user.username,
        'created_at':comp.created_at,
        'cpu_time_seconds':comp.cpu_time_seconds,
        'memory_usage_mb':comp.memory_usage_mb,
        'error_message':comp.error_message,
        'output_log':result.output_log if result else '',
        'convergence_info':result.convergence_info if result else {},
    })
@api_view(['POST'])
@permission_classes([IsAdminUser])
def retry_computation(request,pk):
    comp=cast(Any,Computation.objects.get(pk=pk))
    comp.status='pending'
    comp.error_message=''
    comp.save()
    run_computation_task.delay(comp.pk)
    return Response({'message':'Computation retry started'})
