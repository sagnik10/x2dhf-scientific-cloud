import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
@pytest.fixture
def api_client():
    return APIClient()
@pytest.fixture
def test_user(db):
    return User.objects.create_user(username='testuser',email='test@example.com',password='testpass123')
@pytest.mark.django_db
def test_user_registration(api_client):
    response=api_client.post('/api/auth/users/',{'username':'newuser','email':'new@example.com','password':'newpass123'})
    assert response.status_code==201
@pytest.mark.django_db
def test_duplicate_email_registration_rejected(api_client,test_user):
    response=api_client.post('/api/auth/users/',{'username':'another','email':'TEST@example.com','password':'newpass123'})
    assert response.status_code==400
@pytest.mark.django_db
def test_user_login(api_client,test_user):
    response=api_client.post('/api/auth/jwt/create/',{'email':'test@example.com','password':'testpass123'})
    assert response.status_code==200
    assert 'access' in response.data
@pytest.mark.django_db
def test_login_with_duplicate_email_uses_matching_password(api_client,test_user):
    User.objects.create_user(username='duplicate',email='test@example.com',password='otherpass123')
    response=api_client.post('/api/auth/jwt/create/',{'email':'test@example.com','password':'testpass123'})
    assert response.status_code==200
    assert 'access' in response.data
@pytest.mark.django_db
def test_authenticated_user_profile(api_client,test_user):
    api_client.force_authenticate(user=test_user)
    response=api_client.get('/api/users/users/me/')
    assert response.status_code==200
    assert response.data['username']=='testuser'
