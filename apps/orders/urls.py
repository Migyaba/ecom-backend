from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, check_promo

router = DefaultRouter()
router.register('', OrderViewSet, basename='order')

urlpatterns = [
    path('promo/', check_promo, name='check-promo'),
    path('', include(router.urls)),
]
