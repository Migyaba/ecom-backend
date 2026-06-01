from pathlib import Path
from datetime import timedelta
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # third-party
    'rest_framework',
    'corsheaders',
    'drf_spectacular',
    # local
    'apps.users',
    'apps.products',
    'apps.orders',
    'apps.stores',
    'apps.wishlist',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

AUTH_USER_MODEL = 'users.User'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'DinoMarket API',
    'DESCRIPTION': (
        'API REST du projet DinoMarket — marketplace e-commerce multi-vendeurs.\n\n'
        '## Authentification\n'
        'Toutes les routes protégées utilisent **JWT Bearer Token**.\n'
        '1. Obtenez un token via `POST /api/auth/token/` avec votre email et mot de passe.\n'
        '2. Ajoutez l\'en-tête `Authorization: Bearer <access_token>` à chaque requête.\n'
        '3. Rafraîchissez le token via `POST /api/auth/token/refresh/` avant expiration (60 min).\n\n'
        '## Conventions\n'
        '- Les prix sont en **FCFA** (XOF). Ex : 5 000 = 5 000 FCFA.\n'
        '- Les slugs remplacent les IDs pour les ressources publiques (produits, boutiques, catégories).\n'
        '- La pagination est activée par défaut : `?page=1`, taille de page 20.\n'
        '- Les images uploadées sont servies sous `/media/`.\n'
    ),
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'CONTACT': {'name': 'Miguel Missetcho', 'email': 'm.missetcho@gmail.com'},
    'LICENSE': {'name': 'Propriétaire'},
    'COMPONENT_SPLIT_REQUEST': True,
    'SWAGGER_UI_SETTINGS': {
        'persistAuthorization': True,
        'displayRequestDuration': True,
        'filter': True,
    },
    'TAGS': [
        {'name': 'Auth', 'description': 'Obtention et rafraîchissement des tokens JWT.'},
        {'name': 'Users', 'description': 'Inscription, profil personnel et gestion des adresses.'},
        {'name': 'Stores', 'description': 'Boutiques des vendeurs — lecture publique, création/édition nécessite un compte.'},
        {'name': 'Products', 'description': 'Catalogue de produits, catégories et avis clients.'},
        {'name': 'Orders', 'description': 'Passation et suivi des commandes (accès authentifié uniquement).'},
        {'name': 'Wishlist', 'description': 'Liste de souhaits personnelle (accès authentifié uniquement).'},
    ],
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
}

LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Lagos'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
