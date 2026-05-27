from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import MolecularSystemViewSet,ComputationViewSet
router=DefaultRouter()
router.register('systems',MolecularSystemViewSet,basename='molecular-system')
router.register('jobs',ComputationViewSet,basename='computation')
urlpatterns=[path('',include(router.urls)),]
