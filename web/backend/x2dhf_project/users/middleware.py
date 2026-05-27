from .models import APIAuditLog


class APIAuditLogMiddleware:
    def __init__(self,get_response):
        self.get_response=get_response

    def __call__(self,request):
        response=self.get_response(request)
        user=getattr(request,'user',None)
        if request.path.startswith('/api/') and user and user.is_authenticated:
            forwarded=request.META.get('HTTP_X_FORWARDED_FOR','')
            ip=(forwarded.split(',')[0].strip() if forwarded else request.META.get('REMOTE_ADDR','127.0.0.1')) or '127.0.0.1'
            try:
                APIAuditLog.objects.create(user=user,endpoint=request.path[:255],method=request.method[:10],status_code=getattr(response,'status_code',0),ip_address=ip)
            except Exception:
                pass
        return response
