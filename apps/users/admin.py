from django import forms
from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.db.models import Count
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

from .models import Address, User


class EmailUserCreationForm(UserCreationForm):
    """Le formulaire par défaut vise auth.User ; ici la connexion se fait par e-mail."""

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('email', 'username')


class EmailUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = '__all__'


class AddressInline(TabularInline):
    model = Address
    extra = 0
    fields = ('label', 'full_name', 'line1', 'city', 'country', 'is_default')


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    form = EmailUserChangeForm
    add_form = EmailUserCreationForm
    change_password_form = AdminPasswordChangeForm

    list_display = ('user', 'phone', 'orders_count', 'is_staff', 'is_active', 'date_joined')
    list_display_links = ('user',)
    list_filter = ('is_staff', 'is_active', 'date_joined')
    search_fields = ('email', 'username', 'first_name', 'last_name', 'phone')
    ordering = ('-date_joined',)
    inlines = (AddressInline,)
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Profil', {'fields': ('first_name', 'last_name', 'phone', 'avatar')}),
        ('Droits', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'), 'classes': ('collapse',)}),
        ('Dates', {'fields': ('last_login', 'date_joined'), 'classes': ('collapse',)}),
    )
    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': ('email', 'username', 'password1', 'password2')}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(n_orders=Count('orders'))

    # Création en deux temps (comme le mot de passe) : les adresses s'ajoutent une fois le compte créé
    def get_inlines(self, request, obj):
        return self.inlines if obj else ()

    @display(description='Utilisateur', ordering='email', header=True)
    def user(self, obj):
        return [obj.get_full_name() or obj.username, obj.email]

    @display(description='Commandes', ordering='n_orders')
    def orders_count(self, obj):
        return obj.n_orders


admin.site.unregister(Group)


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass


@admin.register(Address)
class AddressAdmin(ModelAdmin):
    list_display = ('full_name', 'user', 'label', 'city', 'country', 'is_default')
    list_filter = ('country', 'is_default')
    search_fields = ('user__email', 'full_name', 'city')
    autocomplete_fields = ('user',)
