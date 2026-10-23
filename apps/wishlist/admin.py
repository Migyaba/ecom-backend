from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import WishlistItem


@admin.register(WishlistItem)
class WishlistItemAdmin(ModelAdmin):
    list_display = ('user', 'product', 'added_at')
    search_fields = ('user__email', 'product__name')
    autocomplete_fields = ('user', 'product')
    list_select_related = ('user', 'product')
