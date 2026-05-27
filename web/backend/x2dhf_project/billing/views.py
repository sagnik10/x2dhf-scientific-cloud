from rest_framework import viewsets,status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,AllowAny
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import stripe
from django.conf import settings
from django.utils import timezone
from .models import Invoice,Payment,Usage,PricingPlan
from .serializers import InvoiceSerializer,PaymentSerializer,UsageSerializer,PricingPlanSerializer
stripe.api_key=settings.STRIPE_SECRET_KEY
class InvoiceViewSet(viewsets.ModelViewSet):
    serializer_class=InvoiceSerializer
    permission_classes=[IsAuthenticated]
    def get_queryset(self):
        return Invoice.objects.filter(user=self.request.user).order_by('-created_at')
    @action(detail=True,methods=['post'])
    def send(self,request,pk=None):
        invoice=self.get_object()
        invoice.status='sent'
        invoice.save()
        return Response({'message':'Invoice sent'},status=status.HTTP_200_OK)
    @action(detail=True,methods=['post'])
    def pay(self,request,pk=None):
        invoice=self.get_object()
        token=request.data.get('stripe_token')
        try:
            charge=stripe.Charge.create(amount=int(invoice.amount_due*100),currency=invoice.currency.lower(),source=token,description=f"Invoice {invoice.invoice_number}")
            payment=Payment.objects.create(user=request.user,invoice=invoice,stripe_payment_id=charge.id,amount=invoice.amount_due,currency=invoice.currency,status='completed',payment_method='card')
            invoice.status='paid'
            invoice.amount_paid=invoice.amount_due
            invoice.save()
            return Response({'message':'Payment successful','payment_id':payment.id},status=status.HTTP_200_OK)
        except stripe.error.CardError:
            return Response({'error':'Card declined'},status=status.HTTP_400_BAD_REQUEST)
class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class=PaymentSerializer
    permission_classes=[IsAuthenticated]
    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user).order_by('-created_at')
class UsageViewSet(viewsets.ModelViewSet):
    serializer_class=UsageSerializer
    permission_classes=[IsAuthenticated]
    def get_queryset(self):
        return Usage.objects.filter(user=self.request.user)
    @action(detail=False,methods=['get'])
    def current(self,request):
        usage,_=Usage.objects.get_or_create(user=request.user,defaults={'reset_date':timezone.now().date()})
        serializer=self.get_serializer(usage)
        return Response(serializer.data)
class PricingPlanViewSet(viewsets.ModelViewSet):
    queryset=PricingPlan.objects.all()
    serializer_class=PricingPlanSerializer
    permission_classes=[AllowAny]
    def get_permissions(self):
        if self.action in ['list','retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]
@csrf_exempt
def stripe_webhook(request):
    payload=request.body
    sig_header=request.META.get('HTTP_STRIPE_SIGNATURE')
    try:
        event=stripe.Webhook.construct_event(payload,sig_header,settings.STRIPE_WEBHOOK_SECRET)
    except ValueError:
        return JsonResponse({'error':'Invalid payload'},status=400)
    except stripe.error.SignatureVerificationError:
        return JsonResponse({'error':'Invalid signature'},status=400)
    if event['type']=='charge.succeeded':
        charge=event['data']['object']
    elif event['type']=='charge.failed':
        charge=event['data']['object']
    return JsonResponse({'status':'success'})
