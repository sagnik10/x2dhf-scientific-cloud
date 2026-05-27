from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import HealthViewSet,ContactViewSet,DocumentationViewSet,AnalyticsViewSet,PublicAuthViewSet,TheoryPostViewSet,RuntimeControlPresetViewSet
router=DefaultRouter()
router.register('health',HealthViewSet,basename='health')
router.register('contact',ContactViewSet,basename='contact')
router.register('public-auth',PublicAuthViewSet,basename='public-auth')
router.register('docs',DocumentationViewSet,basename='docs')
router.register('analytics',AnalyticsViewSet,basename='analytics')
router.register('theory-posts',TheoryPostViewSet,basename='theory-posts')
router.register('control-presets',RuntimeControlPresetViewSet,basename='control-presets')
urlpatterns=[path('',include(router.urls)),]
