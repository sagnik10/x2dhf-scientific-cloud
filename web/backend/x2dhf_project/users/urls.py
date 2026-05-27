from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet,SubscriptionViewSet
router=DefaultRouter()
router.register('users',UserViewSet,basename='user')
router.register('subscriptions',SubscriptionViewSet,basename='subscription')
urlpatterns=[path('',include(router.urls)),]
