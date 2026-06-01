from django.contrib import admin
from .models import Category, Product, ProductImage, ProductVariant, Review


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'parent')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'store', 'category', 'price', 'badge', 'is_active', 'created_at')
    list_filter = ('badge', 'is_active', 'category')
    search_fields = ('name', 'store__name')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at',)
    inlines = (ProductImageInline, ProductVariantInline)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at')
    list_filter = ('rating',)
    search_fields = ('product__name', 'user__email')
