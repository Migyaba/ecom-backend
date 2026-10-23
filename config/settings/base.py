from pathlib import Path
from datetime import timedelta
import os

from django.templatetags.static import static
from django.urls import reverse_lazy
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY')

INSTALLED_APPS = [
    # Thème de l'admin : doit être chargé avant django.contrib.admin
    'unfold',
    'unfold.contrib.filters',
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
        'DIRS': [BASE_DIR / 'templates'],
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
    'DEFAULT_THROTTLE_RATES': {
        'auth': '10/min',
    },
}

# Codes promo actifs : code → pourcentage de réduction
PROMO_CODES = {
    'DINO10': 10,
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Ecom-backend',
    'DESCRIPTION': (
        'API REST générique pour applications e-commerce multi-vendeurs.\n\n'
        'Conçue pour être consommée par n\'importe quel frontend (React, Vue, mobile, etc.).\n\n'
        '## Authentification\n'
        'Toutes les routes protégées utilisent **JWT Bearer Token**.\n'
        '1. Obtenez un token via `POST /api/auth/token/` avec votre email et mot de passe.\n'
        '2. Ajoutez l\'en-tête `Authorization: Bearer <access_token>` à chaque requête.\n'
        '3. Rafraîchissez le token via `POST /api/auth/token/refresh/` avant expiration (60 min).\n\n'
        '## Conventions\n'
        '- Les prix sont stockés en entiers (FCFA / XOF par défaut). Ex : `5000` = 5 000 FCFA.\n'
        '- Les slugs remplacent les IDs pour les ressources publiques (produits, boutiques, catégories).\n'
        '- La pagination est activée par défaut : `?page=1`, taille de page 20.\n'
        '- Les images uploadées sont servies sous `/media/`.\n'
        '- Les routes 🌐 sont publiques — les routes 🔒 nécessitent un token JWT valide.\n'
    ),
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'CONTACT': {'name': 'Miguel Missetcho', 'email': 'm.missetcho@gmail.com'},
    'LICENSE': {'name': 'MIT'},
    'COMPONENT_SPLIT_REQUEST': True,
    'SWAGGER_UI_SETTINGS': {
        'persistAuthorization': True,
        'displayRequestDuration': True,
        'filter': True,
    },
    'TAGS': [
        {'name': 'Auth',     'description': 'Obtention et rafraîchissement des tokens JWT.'},
        {'name': 'Users',    'description': 'Inscription, profil personnel et gestion des adresses.'},
        {'name': 'Stores',   'description': 'Boutiques des vendeurs — lecture publique, création/édition nécessite un compte.'},
        {'name': 'Products', 'description': 'Catalogue de produits, catégories, témoignages et avis clients.'},
        {'name': 'Orders',   'description': 'Passation et suivi des commandes (accès authentifié uniquement).'},
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
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ── Administration ───────────────────────────────────────────────
# Chemin de l'admin, à personnaliser en production pour ne pas l'exposer sur /admin/
ADMIN_URL = os.environ.get('ADMIN_URL', 'admin/').strip('/') + '/'

# Seuil en dessous duquel un produit est signalé « stock bas » dans l'admin
LOW_STOCK_THRESHOLD = 3

UNFOLD = {
    'SITE_TITLE': 'DinoMarket',
    'SITE_HEADER': 'DinoMarket',
    'SITE_SUBHEADER': 'Administration',
    'SITE_URL': os.environ.get('FRONTEND_URL', 'https://dinomarket.vercel.app'),
    'SITE_ICON': {
        'light': lambda request: static('admin/dinomarket-light.svg'),
        'dark': lambda request: static('admin/dinomarket-dark.svg'),
    },
    'SITE_FAVICONS': [
        {'rel': 'icon', 'type': 'image/svg+xml', 'href': lambda request: static('admin/dinomarket-light.svg')},
    ],
    'SHOW_VIEW_ON_SITE': False,
    'STYLES': [lambda request: static('admin/dinomarket.css')],
    'DASHBOARD_CALLBACK': 'config.admin_dashboard.dashboard_callback',
    'ENVIRONMENT': 'config.admin_dashboard.environment_callback',
    # Or DinoMarket (#C89B3C) comme couleur principale
    'COLORS': {
        'primary': {
            '50': 'oklch(98.5% .015 85)',
            '100': 'oklch(96% .035 85)',
            '200': 'oklch(92% .065 84)',
            '300': 'oklch(86% .1 83)',
            '400': 'oklch(78% .12 81)',
            '500': 'oklch(71% .125 79)',
            '600': 'oklch(62% .115 76)',
            '700': 'oklch(52% .1 73)',
            '800': 'oklch(43% .08 70)',
            '900': 'oklch(36% .065 68)',
            '950': 'oklch(25% .045 65)',
        },
    },
    'SIDEBAR': {
        'show_search': True,
        'show_all_applications': False,
        'navigation': [
            {
                'items': [
                    {'title': 'Tableau de bord', 'icon': 'dashboard', 'link': reverse_lazy('admin:index')},
                ],
            },
            {
                'title': 'Ventes',
                'items': [
                    {
                        'title': 'Commandes',
                        'icon': 'shopping_bag',
                        'link': reverse_lazy('admin:orders_order_changelist'),
                        'badge': 'config.admin_dashboard.pending_orders_badge',
                    },
                ],
            },
            {
                'title': 'Catalogue',
                'items': [
                    {'title': 'Produits', 'icon': 'checkroom', 'link': reverse_lazy('admin:products_product_changelist')},
                    {'title': 'Catégories', 'icon': 'category', 'link': reverse_lazy('admin:products_category_changelist')},
                    {'title': 'Boutiques', 'icon': 'storefront', 'link': reverse_lazy('admin:stores_store_changelist')},
                ],
            },
            {
                'title': 'Clients',
                'items': [
                    {'title': 'Utilisateurs', 'icon': 'person', 'link': reverse_lazy('admin:users_user_changelist')},
                    {'title': 'Adresses', 'icon': 'home_pin', 'link': reverse_lazy('admin:users_address_changelist')},
                    {'title': 'Listes de souhaits', 'icon': 'favorite', 'link': reverse_lazy('admin:wishlist_wishlistitem_changelist')},
                ],
            },
            {
                'title': 'Contenu',
                'items': [
                    {'title': 'Avis clients', 'icon': 'reviews', 'link': reverse_lazy('admin:products_review_changelist')},
                    {'title': 'Témoignages', 'icon': 'format_quote', 'link': reverse_lazy('admin:products_testimonial_changelist')},
                ],
            },
            {
                'title': 'Accès',
                'items': [
                    {'title': 'Groupes', 'icon': 'group', 'link': reverse_lazy('admin:auth_group_changelist')},
                ],
            },
        ],
    },
}
