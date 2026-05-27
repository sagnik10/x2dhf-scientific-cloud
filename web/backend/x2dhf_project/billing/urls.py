from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import InvoiceViewSet,PaymentViewSet,UsageViewSet,PricingPlanViewSet,stripe_webhook
router=DefaultRouter()
router.register('invoices',InvoiceViewSet,basename='invoice')
router.register('payments',PaymentViewSet,basename='payment')
router.register('usage',UsageViewSet,basename='usage')
router.register('pricing',PricingPlanViewSet,basename='pricing')
urlpatterns=[path('',include(router.urls)),path('webhook/stripe/',stripe_webhook,name='stripe_webhook'),]
