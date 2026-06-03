from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes
from .models import Category, Product, ProductImage, ProductVariant, Review, Testimonial


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'parent', 'eyebrow', 'tone', 'cover_url')


class ProductImageSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ('id', 'image', 'image_url', 'url', 'order', 'is_cover')

    def get_url(self, obj):
        if obj.image:
            return self.context['request'].build_absolute_uri(obj.image.url)
        return obj.image_url or None


class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ('id', 'size', 'color', 'stock')


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ('id', 'author', 'rating', 'body', 'created_at')
        read_only_fields = ('id', 'author', 'created_at')

    def get_author(self, obj):
        full = obj.user.get_full_name().strip()
        if full:
            return full
        # Fallback : prénom depuis l'email (avant le @)
        return obj.user.email.split('@')[0].replace('.', ' ').replace('_', ' ').title()

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        validated_data['product'] = self.context['product']
        return super().create(validated_data)


class ProductListSerializer(serializers.ModelSerializer):
    """Serializer allégé pour les grilles de listing."""
    cover = serializers.SerializerMethodField()
    store_name = serializers.CharField(source='store.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Product
        fields = ('id', 'slug', 'name', 'store_name', 'category_name', 'price', 'original_price', 'badge', 'sale_ends_at', 'cover')

    @extend_schema_field(OpenApiTypes.URI)
    def get_cover(self, obj):
        img = obj.images.filter(is_cover=True).first() or obj.images.first()
        if not img:
            return None
        if img.image:
            return self.context['request'].build_absolute_uri(img.image.url)
        return img.image_url or None


class ProductDetailSerializer(serializers.ModelSerializer):
    """Serializer complet pour la fiche produit."""
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    store_name = serializers.CharField(source='store.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    avg_rating = serializers.SerializerMethodField()
    is_on_sale = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            'id', 'slug', 'name', 'description', 'store_name', 'category_name',
            'price', 'original_price', 'badge', 'is_on_sale',
            'images', 'variants', 'reviews', 'avg_rating',
        )

    @extend_schema_field(OpenApiTypes.FLOAT)
    def get_avg_rating(self, obj):
        reviews = obj.reviews.all()
        if not reviews:
            return None
        return round(sum(r.rating for r in reviews) / len(reviews), 1)

    @extend_schema_field(OpenApiTypes.BOOL)
    def get_is_on_sale(self, obj):
        return obj.is_on_sale


class TestimonialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testimonial
        fields = ('id', 'name', 'city', 'text', 'product_name', 'rating', 'tone')
