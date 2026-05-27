from celery import shared_task
from django.utils import timezone
from django.db.models import F
from .models import Computation
from results.models import ComputationResult
from users.models import UserProfile
from .services import run_engine
import subprocess

def error_text(error):
    messages=getattr(error,'messages',None)
    if messages:
        return '\n'.join(str(item) for item in messages)
    return str(error)

@shared_task(bind=True)
def run_computation_task(self,computation_id):
    computation=None
    try:
        computation=Computation.objects.get(id=computation_id)
        computation.status='running'
        computation.started_at=timezone.now()
        computation.task_id=self.request.id or ''
        computation.save()
        result=run_engine(computation)
        computation.cpu_time_seconds=result['elapsed']
        computation.completed_at=timezone.now()
        if result['ok']:
            computation.status='completed'
            values=result.get('values',{})
            ComputationResult.objects.update_or_create(computation=computation,defaults={'user':computation.user,'output_log':result.get('stdout',''),'convergence_info':result.get('convergence',{}),**values})
            UserProfile.objects.filter(user=computation.user).update(monthly_computations=F('monthly_computations')+1)
        else:
            computation.status='failed'
            computation.error_message=result.get('stderr') or 'Unknown error'
            ComputationResult.objects.update_or_create(computation=computation,defaults={'user':computation.user,'output_log':result.get('stdout',''),'convergence_info':result.get('convergence',{})})
        computation.save()
        return {'computation_id':computation_id,'status':computation.status}
    except Computation.DoesNotExist:
        return {'error':'Computation not found'}
    except subprocess.TimeoutExpired:
        if computation:
            computation.status='failed'
            computation.error_message='Computation timed out'
            computation.completed_at=timezone.now()
            computation.save()
        return {'error':'Computation timeout'}
    except Exception as e:
        message=error_text(e)
        if computation:
            computation.status='failed'
            computation.error_message=message
            computation.completed_at=timezone.now()
            computation.save()
            ComputationResult.objects.update_or_create(computation=computation,defaults={'user':computation.user,'output_log':message,'convergence_info':{'runtime':{'final':True,'error':message}}})
        return {'error':message}
