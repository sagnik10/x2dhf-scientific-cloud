import os
import sys
from pathlib import Path
from datetime import timedelta
from decouple import config
BASE_DIR=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(BASE_DIR/'x2dhf_project'))
REPO_ROOT=BASE_DIR.parent.parent
FRONTEND_BUILD_DIR=REPO_ROOT/'web'/'frontend'/'build'
TESTING='pytest' in sys.argv
SECRET_KEY=config('SECRET_KEY','django-insecure-dev-key-change-in-production')
def cast_bool(value):
    return str(value).strip().lower() in ['1','true','yes','on','debug','development','dev']
DEBUG=config('DEBUG',default=True,cast=cast_bool)
ALLOWED_HOSTS=config('ALLOWED_HOSTS','localhost,127.0.0.1,*.vercel.app,*.railway.app').split(',')
INSTALLED_APPS=['django.contrib.admin','django.contrib.auth','django.contrib.contenttypes','django.contrib.sessions','django.contrib.messages','django.contrib.staticfiles','rest_framework','corsheaders','django_filters','django_extensions','users','computations','results','billing','core.apps.CoreConfig',]
MIDDLEWARE=['django.middleware.security.SecurityMiddleware','whitenoise.middleware.WhiteNoiseMiddleware','django.contrib.sessions.middleware.SessionMiddleware','corsheaders.middleware.CorsMiddleware','django.middleware.common.CommonMiddleware','django.middleware.csrf.CsrfViewMiddleware','django.contrib.auth.middleware.AuthenticationMiddleware','users.middleware.APIAuditLogMiddleware','django.contrib.messages.middleware.MessageMiddleware','django.middleware.clickjacking.XFrameOptionsMiddleware',]
ROOT_URLCONF='x2dhf_project.urls'
TEMPLATES=[{'BACKEND':'django.template.backends.django.DjangoTemplates','DIRS':[BASE_DIR/'templates'],'APP_DIRS':True,'OPTIONS':{'context_processors':['django.template.context_processors.debug','django.template.context_processors.request','django.contrib.auth.context_processors.auth','django.contrib.messages.context_processors.messages',],},},]
WSGI_APPLICATION='x2dhf_project.wsgi.application'
DB_ENGINE=config('DB_ENGINE','sqlite')
if DB_ENGINE=='postgresql':
    DATABASES={'default':{'ENGINE':'django.db.backends.postgresql','NAME':config('DB_NAME','x2dhf_db'),'USER':config('DB_USER','postgres'),'PASSWORD':config('DB_PASSWORD','postgres'),'HOST':config('DB_HOST','localhost'),'PORT':config('DB_PORT','5432'),},}
else:
    DATABASES={'default':{'ENGINE':'django.db.backends.sqlite3','NAME':BASE_DIR/'db.sqlite3',},}
AUTH_PASSWORD_VALIDATORS=[{'NAME':'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},{'NAME':'django.contrib.auth.password_validation.MinimumLengthValidator',},{'NAME':'django.contrib.auth.password_validation.CommonPasswordValidator',},{'NAME':'django.contrib.auth.password_validation.NumericPasswordValidator',},]
LANGUAGE_CODE='en-us'
TIME_ZONE='UTC'
USE_I18N=True
USE_TZ=True
STATIC_URL='/static/'
STATIC_ROOT=BASE_DIR/'staticfiles'
STATICFILES_DIRS=[FRONTEND_BUILD_DIR/'static'] if (FRONTEND_BUILD_DIR/'static').exists() else []
MEDIA_URL='/media/'
MEDIA_ROOT=BASE_DIR/'media'
STORAGES={'default':{'BACKEND':'django.core.files.storage.FileSystemStorage'},'staticfiles':{'BACKEND':'whitenoise.storage.CompressedManifestStaticFilesStorage'}}
DEFAULT_AUTO_FIELD='django.db.models.BigAutoField'
REST_FRAMEWORK={'DEFAULT_AUTHENTICATION_CLASSES':('rest_framework_simplejwt.authentication.JWTAuthentication',),'DEFAULT_PERMISSION_CLASSES':('rest_framework.permissions.IsAuthenticated',),'DEFAULT_PAGINATION_CLASS':'rest_framework.pagination.PageNumberPagination','PAGE_SIZE':20,'DEFAULT_FILTER_BACKENDS':['django_filters.rest_framework.DjangoFilterBackend','rest_framework.filters.SearchFilter','rest_framework.filters.OrderingFilter',],'DEFAULT_THROTTLE_CLASSES':['rest_framework.throttling.AnonRateThrottle','rest_framework.throttling.UserRateThrottle',],'DEFAULT_THROTTLE_RATES':{'anon':'100/hour','user':'1000/hour',},}
SIMPLE_JWT={'ACCESS_TOKEN_LIFETIME':timedelta(hours=24),'REFRESH_TOKEN_LIFETIME':timedelta(days=7),'ROTATE_REFRESH_TOKENS':True,'BLACKLIST_AFTER_ROTATION':True,'ALGORITHM':'HS256','SIGNING_KEY':SECRET_KEY,'VERIFYING_KEY':None,'AUDIENCE':None,'ISSUER':None,'JTI_CLAIM':'jti','TOKEN_TYPE_CLAIM':'token_type','USER_ID_FIELD':'id','USER_ID_CLAIM':'user_id','USER_AUTHENTICATION_RULE':'rest_framework_simplejwt.authentication.default_user_authentication_rule','AUTH_TOKEN_CLASSES':('rest_framework_simplejwt.tokens.AccessToken',),'TOKEN_USER_CLASS':'django.contrib.auth.models.User',}
CORS_ALLOWED_ORIGINS=config('CORS_ALLOWED_ORIGINS','http://localhost:3000,http://127.0.0.1:3000').split(',')
CORS_ALLOW_CREDENTIALS=True
CELERY_BROKER_URL=config('CELERY_BROKER_URL','redis://localhost:6379/0')
CELERY_RESULT_BACKEND=config('CELERY_RESULT_BACKEND','redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT=['json']
CELERY_TASK_SERIALIZER='json'
CELERY_RESULT_SERIALIZER='json'
CELERY_TIMEZONE='UTC'
CELERY_TASK_ALWAYS_EAGER=config('CELERY_TASK_ALWAYS_EAGER',True,cast=cast_bool)
CELERY_TASK_EAGER_PROPAGATES=config('CELERY_TASK_EAGER_PROPAGATES',False,cast=cast_bool)
AUTO_START_COMPUTATIONS=config('AUTO_START_COMPUTATIONS',not TESTING,cast=cast_bool)
PYTHON_SCIENCE_RUNTIME=config('PYTHON_SCIENCE_RUNTIME',True,cast=cast_bool)
USE_NATIVE_X2DHF=config('USE_NATIVE_X2DHF',False,cast=cast_bool)
STRIPE_PUBLIC_KEY=config('STRIPE_PUBLIC_KEY','')
STRIPE_SECRET_KEY=config('STRIPE_SECRET_KEY','')
STRIPE_WEBHOOK_SECRET=config('STRIPE_WEBHOOK_SECRET','')
DEFAULT_X2DHF_BINARY=REPO_ROOT/'bin'/'xhf'
X2DHF_DIRECTORY=config('X2DHF_DIRECTORY',str(REPO_ROOT))
X2DHF_BINARY_PATH=config('X2DHF_BINARY_PATH',str(DEFAULT_X2DHF_BINARY))
QE_BINARY_PATH=config('QE_BINARY_PATH','/usr/local/bin/pw.x')
LIBXC_LIBRARY_PATH=config('LIBXC_LIBRARY_PATH','')
PSEUDO_DIR=config('PSEUDO_DIR','/opt/pseudopotentials')
COMPUTATION_WORKDIR=config('COMPUTATION_WORKDIR',str(BASE_DIR/'job_workdir'))
MAX_COMPUTATION_TIME=config('MAX_COMPUTATION_TIME',3600,cast=int)
MAX_GRID_SIZE=config('MAX_GRID_SIZE',1000,cast=int)
STORAGE_QUOTA_GB=config('STORAGE_QUOTA_GB',10,cast=int)
ADMIN_EMAIL=config('ADMIN_EMAIL','admin@x2dhf.com')
DJOSER={'LOGIN_FIELD':'email','USER_CREATE_PASSWORD_RETYPE':False,'SERIALIZERS':{'user_create':'users.auth_serializers.UserCreateSerializer','current_user':'djoser.serializers.UserSerializer'}}
