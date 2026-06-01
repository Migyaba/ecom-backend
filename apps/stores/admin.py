from django.contrib import admin
from .models import Store


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'city', 'country', 'is_active', 'created_at')
    list_filter = ('is_active', 'country')
    search_fields = ('name', 'owner__email')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at',)
