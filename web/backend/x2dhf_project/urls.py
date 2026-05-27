from django.contrib import admin
from django.urls import path,include,re_path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenRefreshView,TokenVerifyView
from users.auth_views import EmailTokenObtainPairView
from core.spa import ReactAppView,ReactAssetView
urlpatterns=[path('admin/',admin.site.urls),path('api/auth/',include('djoser.urls')),path('api/auth/jwt/create/',EmailTokenObtainPairView.as_view(),name='jwt-create'),path('api/auth/jwt/refresh/',TokenRefreshView.as_view(),name='jwt-refresh'),path('api/auth/jwt/verify/',TokenVerifyView.as_view(),name='jwt-verify'),path('api/users/',include('users.urls')),path('api/computations/',include('computations.urls')),path('api/results/',include('results.urls')),path('api/billing/',include('billing.urls')),path('api/core/',include('core.urls')),]
urlpatterns+=[path('favicon.png',ReactAssetView.as_view(),{'path':'favicon.png'}),re_path(r'^(?!api/|admin/|media/|static/).*$' ,ReactAppView.as_view(),name='react-app')]
if settings.DEBUG:
    urlpatterns+=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
