from pathlib import Path
from django.conf import settings
from django.http import FileResponse,Http404
from django.views import View

class ReactAppView(View):
    def get(self,request,*args,**kwargs):
        index=Path(settings.FRONTEND_BUILD_DIR)/'index.html'
        if not index.exists():
            raise Http404('React build not found. Run npm run build in web/frontend.')
        return FileResponse(index.open('rb'),content_type='text/html')

class ReactAssetView(View):
    def get(self,request,path,*args,**kwargs):
        target=(Path(settings.FRONTEND_BUILD_DIR)/path).resolve()
        root=Path(settings.FRONTEND_BUILD_DIR).resolve()
        if not str(target).startswith(str(root)) or not target.exists() or not target.is_file():
            raise Http404()
        return FileResponse(target.open('rb'))
