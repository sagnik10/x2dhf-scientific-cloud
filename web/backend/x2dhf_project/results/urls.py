from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import ComputationResultViewSet,ResultVisualizationViewSet,ExportViewSet
router=DefaultRouter()
router.register('results',ComputationResultViewSet,basename='result')
router.register('visualizations',ResultVisualizationViewSet,basename='visualization')
router.register('exports',ExportViewSet,basename='export')
urlpatterns=[path('',include(router.urls)),]
