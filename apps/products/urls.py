from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ProductViewSet, ReviewCreateView, TestimonialListView

router = DefaultRouter()
router.register('categories', CategoryViewSet, basename='category')
router.register('', ProductViewSet, basename='product')

urlpatterns = [
    path('<slug:slug>/reviews/', ReviewCreateView.as_view(), name='product-review'),
    path('testimonials/', TestimonialListView.as_view(), name='testimonials'),
    path('', include(router.urls)),
]
