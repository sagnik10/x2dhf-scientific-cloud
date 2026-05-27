from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from djoser.serializers import UserCreateSerializer as DjoserUserCreateSerializer
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class UserCreateSerializer(DjoserUserCreateSerializer):
    class Meta(DjoserUserCreateSerializer.Meta):
        model=User
        fields=('id','username','email','password')

    def validate_email(self,value):
        email=str(value).strip().lower()
        if not email:
            raise serializers.ValidationError('Email is required')
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError('An account with this email already exists')
        return email

class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field='email'

    def validate(self,attrs):
        email=str(attrs.get('email','')).strip()
        password=attrs.get('password')
        users=User.objects.filter(email__iexact=email,is_active=True).order_by('id')
        if not users.exists():
            raise serializers.ValidationError('No active account found with the given credentials')
        self.user=None
        for user in users:
            authenticated=authenticate(username=user.username,password=password)
            if authenticated is not None:
                self.user=authenticated
                break
        if self.user is None:
            raise serializers.ValidationError('No active account found with the given credentials')
        data={}
        refresh=self.get_token(self.user)
        data['refresh']=str(refresh)
        data['access']=str(refresh.access_token)
        return data
