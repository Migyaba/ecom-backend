from django.conf import settings
from django.contrib import admin, messages
from django.db.models import Count, Sum
from django.db.models.functions import Coalesce
from django.utils.html import format_html
from unfold.admin import ModelAdmin, TabularInline
from unfold.contrib.filters.admin import RelatedDropdownFilter
from unfold.decorators import action, display

from config.admin_utils import badge, format_fcfa, header_with_image
from .models import Category, Product, ProductImage, ProductVariant, Review, Testimonial


def image_src(img):
    if img is None:
        return None
    if img.image:
        return img.image.url
    return img.image_url or None


class ProductImageInline(TabularInline):
    model = ProductImage
    extra = 1
    fields = ('preview', 'image', 'image_url', 'order', 'is_cover')
    readonly_fields = ('preview',)
    ordering = ('order',)

    @display(description='Aperçu')
    def preview(self, obj):
        src = image_src(obj) if obj.pk else None
        if not src:
            return '—'
        return format_html('<img src="{}" style="height:64px;width:64px;object-fit:cover;border-radius:6px">', src)


class ProductVariantInline(TabularInline):
    model = ProductVariant
    extra = 1
    fields = ('size', 'color', 'stock')


class StockFilter(admin.SimpleListFilter):
    title = 'stock'
    parameter_name = 'stock'

    def lookups(self, request, model_admin):
        return (('out', 'Rupture'), ('low', 'Stock bas'), ('ok', 'En stock'))

    def queryset(self, request, queryset):
        threshold = settings.LOW_STOCK_THRESHOLD
        if self.value() == 'out':
            return queryset.filter(total_stock=0)
        if self.value() == 'low':
            return queryset.filter(total_stock__gt=0, total_stock__lte=threshold)
        if self.value() == 'ok':
            return queryset.filter(total_stock__gt=threshold)
        return queryset


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ('category', 'slug', 'eyebrow', 'tone', 'parent', 'products_count')
    list_display_links = ('category',)
    list_editable = ('tone', 'eyebrow')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('parent').annotate(n_products=Count('products'))

    @display(description='Catégorie', ordering='name', header=True)
    def category(self, obj):
        return header_with_image(obj.name, obj.eyebrow, obj.cover_url)

    @display(description='Produits', ordering='n_products')
    def products_count(self, obj):
        return obj.n_products


@admin.register(Product)
class ProductAdmin(ModelAdmin):
    list_display = ('product', 'category', 'price_display', 'stock_badge', 'badge', 'is_active', 'created_at')
    list_display_links = ('product',)
    list_editable = ('is_active',)
    list_filter = (
        StockFilter,
        'is_active',
        'badge',
        ('category', RelatedDropdownFilter),
        ('store', RelatedDropdownFilter),
    )
    list_filter_submit = True
    search_fields = ('name', 'slug', 'store__name')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at',)
    autocomplete_fields = ('store',)
    list_per_page = 30
    inlines = (ProductImageInline, ProductVariantInline)
    fieldsets = (
        (None, {'fields': ('name', 'slug', 'store', 'category', 'description', 'is_active')}),
        ('Prix et promotion', {'fields': ('price', 'original_price', 'badge', 'sale_ends_at')}),
        ('Informations', {'fields': ('created_at',), 'classes': ('collapse',)}),
    )
    actions = ('activate', 'deactivate')

    def get_queryset(self, request):
        return (
            super().get_queryset(request)
            .select_related('store', 'category')
            .prefetch_related('images')
            .annotate(total_stock=Coalesce(Sum('variants__stock'), 0))
        )

    @display(description='Produit', ordering='name', header=True)
    def product(self, obj):
        images = list(obj.images.all())
        cover = next((i for i in images if i.is_cover), images[0] if images else None)
        return header_with_image(obj.name, obj.store.name, image_src(cover))

    @display(description='Prix', ordering='price')
    def price_display(self, obj):
        if obj.original_price and obj.original_price > obj.price:
            return format_html('{} <s style="opacity:.5">{}</s>', format_fcfa(obj.price), format_fcfa(obj.original_price))
        return format_fcfa(obj.price)

    @display(description='Stock', ordering='total_stock')
    def stock_badge(self, obj):
        if obj.total_stock == 0:
            return badge('Rupture', 'danger')
        if obj.total_stock <= settings.LOW_STOCK_THRESHOLD:
            return badge(f'{obj.total_stock} restant(s)', 'warning')
        return badge(str(obj.total_stock), 'success')

    @action(description='Activer (visible sur le site)', permissions=['change'])
    def activate(self, request, queryset):
        messages.success(request, f'{queryset.update(is_active=True)} produit(s) activé(s).')

    @action(description='Désactiver (masquer du site)', permissions=['change'])
    def deactivate(self, request, queryset):
        messages.success(request, f'{queryset.update(is_active=False)} produit(s) masqué(s).')


@admin.register(Review)
class ReviewAdmin(ModelAdmin):
    list_display = ('product', 'author', 'stars', 'excerpt', 'created_at')
    list_filter = ('rating', ('product', RelatedDropdownFilter))
    list_filter_submit = True
    search_fields = ('product__name', 'user__email', 'body')
    readonly_fields = ('product', 'user', 'rating', 'body', 'created_at')

    def has_add_permission(self, request):
        return False

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('product', 'user')

    @display(description='Auteur', ordering='user__email')
    def author(self, obj):
        return obj.user.get_full_name() or obj.user.email

    @display(description='Note', ordering='rating', label={1: 'danger', 2: 'danger', 3: 'warning', 4: 'success', 5: 'success'})
    def stars(self, obj):
        return obj.rating, '★' * obj.rating

    @display(description='Avis')
    def excerpt(self, obj):
        return obj.body if len(obj.body) <= 80 else obj.body[:80] + '…'


@admin.register(Testimonial)
class TestimonialAdmin(ModelAdmin):
    list_display = ('name', 'city', 'product_name', 'rating', 'tone', 'is_active', 'created_at')
    list_editable = ('is_active', 'tone')
    list_filter = ('is_active', 'rating')
    search_fields = ('name', 'city', 'text', 'product_name')
