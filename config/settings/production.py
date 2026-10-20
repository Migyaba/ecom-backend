from .base import *
import os

DEBUG = False

# WhiteNoise sert les fichiers statiques (admin, Swagger) directement depuis Gunicorn
MIDDLEWARE.insert(MIDDLEWARE.index('django.middleware.security.SecurityMiddleware') + 1, 'whitenoise.middleware.WhiteNoiseMiddleware')
# Fichiers uploadés (images produits, avatars, logos) stockés dans MinIO (API compatible S3)
STORAGES = {
    'default': {
        'BACKEND': 'storages.backends.s3.S3Storage',
        'OPTIONS': {
            'endpoint_url': os.environ.get('MINIO_ENDPOINT_URL'),
            'access_key': os.environ.get('MINIO_ACCESS_KEY'),
            'secret_key': os.environ.get('MINIO_SECRET_KEY'),
            'bucket_name': os.environ.get('MINIO_BUCKET', 'ecom-media'),
            'region_name': os.environ.get('MINIO_REGION', 'us-east-1'),
            'addressing_style': 'path',
            'signature_version': 's3v4',
            # Bucket en lecture publique : URLs stables, sans signature
            'querystring_auth': False,
            'default_acl': None,
            'file_overwrite': False,
            # Domaine public du bucket (ex. minio.mondomaine.com/ecom-media), sans https://
            'custom_domain': os.environ.get('MINIO_PUBLIC_DOMAIN') or None,
            'url_protocol': 'https:',
        },
    },
    'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage'},
}

ALLOWED_HOSTS = [h.strip() for h in os.environ.get('ALLOWED_HOSTS', '').split(',') if h.strip()]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

CORS_ALLOWED_ORIGINS = [o.strip() for o in os.environ.get('CORS_ALLOWED_ORIGINS', '').split(',') if o.strip()]

# Derrière le reverse proxy (Traefik), HTTPS est signalé par cet en-tête
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SECURE_REDIRECT_EXEMPT = [r'^healthz/$']
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CSRF_TRUSTED_ORIGINS = [f'https://{h}' for h in ALLOWED_HOSTS]

SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
