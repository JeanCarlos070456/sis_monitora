import os
from pathlib import Path
from urllib.parse import urlparse,unquote
from dotenv import load_dotenv
BASE_DIR=Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR/'.env')
DEBUG=os.getenv('DEBUG','false').lower()=='true'
SECRET_KEY=os.getenv('DJANGO_SECRET_KEY','NOT-FOR-PRODUCTION-CHANGE-ME')
if not DEBUG and SECRET_KEY=='NOT-FOR-PRODUCTION-CHANGE-ME':
 raise RuntimeError('Configure DJANGO_SECRET_KEY para produção')
ALLOWED_HOSTS=[s.strip() for s in os.getenv('ALLOWED_HOSTS','localhost,127.0.0.1').split(',') if s.strip()]
CSRF_TRUSTED_ORIGINS=[s.strip() for s in os.getenv('CSRF_TRUSTED_ORIGINS','').split(',') if s.strip()]
INSTALLED_APPS=['django.contrib.admin','django.contrib.auth','django.contrib.contenttypes','django.contrib.sessions','django.contrib.messages','django.contrib.staticfiles','core']
MIDDLEWARE=['django.middleware.security.SecurityMiddleware','whitenoise.middleware.WhiteNoiseMiddleware','django.contrib.sessions.middleware.SessionMiddleware','django.middleware.common.CommonMiddleware','django.middleware.csrf.CsrfViewMiddleware','django.contrib.auth.middleware.AuthenticationMiddleware','django.contrib.messages.middleware.MessageMiddleware','django.middleware.clickjacking.XFrameOptionsMiddleware']
ROOT_URLCONF='config.urls'
TEMPLATES=[{'BACKEND':'django.template.backends.django.DjangoTemplates','DIRS':[BASE_DIR/'templates'],'APP_DIRS':True,'OPTIONS':{'context_processors':['django.template.context_processors.debug','django.template.context_processors.request','django.contrib.auth.context_processors.auth','django.contrib.messages.context_processors.messages','core.context.app_settings']}}]
WSGI_APPLICATION='config.wsgi.application'
url=os.getenv('DATABASE_URL','')
if url:
 u=urlparse(url)
 if u.scheme not in ('postgres','postgresql'): raise RuntimeError('DATABASE_URL deve usar PostgreSQL')
 DATABASES={'default':{'ENGINE':'django.db.backends.postgresql','NAME':unquote(u.path.lstrip('/')),'USER':unquote(u.username or ''),'PASSWORD':unquote(u.password or ''),'HOST':u.hostname,'PORT':u.port or 5432,'OPTIONS':{'sslmode':'require'} if os.getenv('DB_SSLMODE','require')=='require' else {}}}
else:
 if os.getenv('SIS_DEMO_MODE','false').lower()!='true':raise RuntimeError('Configure DATABASE_URL ou habilite SIS_DEMO_MODE=true para testes locais')
 DATABASES={'default':{'ENGINE':'django.db.backends.sqlite3','NAME':BASE_DIR/'db.sqlite3'}}
AUTH_PASSWORD_VALIDATORS=[{'NAME':'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},{'NAME':'django.contrib.auth.password_validation.MinimumLengthValidator'},{'NAME':'django.contrib.auth.password_validation.CommonPasswordValidator'},{'NAME':'django.contrib.auth.password_validation.NumericPasswordValidator'}]
LANGUAGE_CODE='pt-br'; TIME_ZONE='America/Sao_Paulo'; USE_I18N=True; USE_TZ=True
STATIC_URL='static/'; STATICFILES_DIRS=[BASE_DIR/'static'];STATIC_ROOT=BASE_DIR/'staticfiles'
STORAGES={'staticfiles':{'BACKEND':'whitenoise.storage.CompressedManifestStaticFilesStorage'}}
DEFAULT_AUTO_FIELD='django.db.models.BigAutoField'
LOGIN_URL='login'; LOGIN_REDIRECT_URL='dashboard';LOGOUT_REDIRECT_URL='login'
SESSION_COOKIE_HTTPONLY=True;CSRF_COOKIE_HTTPONLY=True
SESSION_COOKIE_SECURE=not DEBUG;CSRF_COOKIE_SECURE=not DEBUG
SECURE_PROXY_SSL_HEADER=('HTTP_X_FORWARDED_PROTO','https')
X_FRAME_OPTIONS='DENY';SECURE_CONTENT_TYPE_NOSNIFF=True
FILE_UPLOAD_MAX_MEMORY_SIZE=10*1024*1024
DATA_UPLOAD_MAX_MEMORY_SIZE=15*1024*1024
SIS_DEMO_MODE=os.getenv('SIS_DEMO_MODE','false').lower()=='true'
SUPABASE_URL=os.getenv('SUPABASE_URL','').rstrip('/')
SUPABASE_ANON_KEY=os.getenv('SUPABASE_ANON_KEY','')
GEMINI_API_KEY=os.getenv('GEMINI_API_KEY','')
GEMINI_MODEL=os.getenv('GEMINI_MODEL','gemini-2.5-flash')
