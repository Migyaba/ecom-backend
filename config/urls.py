from django.contrib import admin
from django.http import JsonResponse
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.throttling import ScopedRateThrottle
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from drf_spectacular.utils import extend_schema


@extend_schema(
    tags=['Auth'],
    summary='Obtenir un token JWT',
    description=(
        'Authentifiez-vous avec votre **email** et **mot de passe** pour recevoir '
        'un couple de tokens JWT.\n\n'
        '- `access` : valide **60 minutes**, à transmettre dans `Authorization: Bearer <token>`.\n'
        '- `refresh` : valide **7 jours**, à utiliser pour renouveler l\'access token.\n\n'
        '**Exemple de corps de requête :**\n'
        '```json\n{"email": "user@example.com", "password": "motdepasse"}\n```'
    ),
)
class TokenObtainView(TokenObtainPairView):
    throttle_classes = (ScopedRateThrottle,)
    throttle_scope = 'auth'


@extend_schema(
    tags=['Auth'],
    summary='Rafraîchir le token d\'accès',
    description=(
        'Échangez un **refresh token** valide contre un nouveau **access token**.\n\n'
        'À appeler avant l\'expiration de l\'access token (60 min) pour maintenir la session.\n\n'
        '**Exemple de corps de requête :**\n'
        '```json\n{"refresh": "<refresh_token>"}\n```'
    ),
)
class TokenRefreshView(TokenRefreshView):
    pass


def healthz(request):
    return JsonResponse({'status': 'ok'})


urlpatterns = [
    path('healthz/', healthz, name='healthz'),
    path('admin/', admin.site.urls),

    # Auth JWT
    path('api/auth/token/', TokenObtainView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Apps
    path('api/users/', include('apps.users.urls')),
    path('api/products/', include('apps.products.urls')),
    path('api/orders/', include('apps.orders.urls')),
    path('api/stores/', include('apps.stores.urls')),
    path('api/wishlist/', include('apps.wishlist.urls')),

    # Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
