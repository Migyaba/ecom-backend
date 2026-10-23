from django.contrib import admin
from django.db.models import Count
from unfold.admin import ModelAdmin
from unfold.decorators import display

from config.admin_utils import header_with_image

from .models import Store


@admin.register(Store)
class StoreAdmin(ModelAdmin):
    list_display = ('store', 'city', 'country', 'products_count', 'is_active', 'created_at')
    list_display_links = ('store',)
    list_editable = ('is_active',)
    list_filter = ('is_active', 'country')
    search_fields = ('name', 'owner__email')
    prepopulated_fields = {'slug': ('name',)}
    autocomplete_fields = ('owner',)
    readonly_fields = ('created_at',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('owner').annotate(n_products=Count('products'))

    @display(description='Boutique', ordering='name', header=True)
    def store(self, obj):
        return header_with_image(obj.name, obj.owner.email, obj.logo.url if obj.logo else None)

    @display(description='Produits', ordering='n_products')
    def products_count(self, obj):
        return obj.n_products
