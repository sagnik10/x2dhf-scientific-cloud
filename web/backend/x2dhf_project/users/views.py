from rest_framework import viewsets,status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,AllowAny
from django.contrib.auth.models import User
from .models import UserProfile,Subscription,APIAuditLog
from .serializers import UserSerializer,UserProfileSerializer,UserDetailSerializer,SubscriptionSerializer
from .models import generate_api_key
from datetime import datetime
import uuid
class UserViewSet(viewsets.ModelViewSet):
    queryset=User.objects.all()
    serializer_class=UserDetailSerializer
    permission_classes=[IsAuthenticated]
    @action(detail=False,methods=['get','patch'])
    def me(self,request):
        if request.method=='PATCH':
            user=request.user
            for field in ['first_name','last_name']:
                if field in request.data:
                    setattr(user,field,request.data.get(field,''))
            user.save(update_fields=['first_name','last_name'])
            profile_data=request.data.get('profile') or {}
            organization=request.data.get('organization',profile_data.get('organization'))
            if organization is not None:
                user.profile.organization=organization
                user.profile.save(update_fields=['organization'])
        serializer=self.get_serializer(request.user)
        return Response(serializer.data)
    @action(detail=False,methods=['post'])
    def generate_api_key(self,request):
        profile=request.user.profile
        profile.api_key=generate_api_key()
        profile.save()
        return Response({'api_key':profile.api_key})
    @action(detail=False,methods=['get'])
    def usage(self,request):
        profile=request.user.profile
        return Response({'storage_used_gb':profile.storage_used_gb,'monthly_computations':profile.monthly_computations,'plan':profile.plan})
class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset=Subscription.objects.all()
    serializer_class=SubscriptionSerializer
    permission_classes=[IsAuthenticated]
    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)
    @action(detail=False,methods=['post'])
    def upgrade(self,request):
        plan=request.data.get('plan')
        if plan not in ['pro','enterprise']:
            return Response({'error':'Invalid plan'},status=status.HTTP_400_BAD_REQUEST)
        subscription=request.user.subscription
        subscription.plan=plan
        subscription.save()
        return Response({'message':'Subscription updated'},status=status.HTTP_200_OK)
