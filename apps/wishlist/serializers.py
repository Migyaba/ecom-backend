from rest_framework import serializers
from apps.products.models import Product
from apps.products.serializers import ProductListSerializer
from .models import WishlistItem


class WishlistItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = WishlistItem
        fields = ('id', 'product', 'product_id', 'added_at')
        read_only_fields = ('id', 'added_at')

    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value, is_active=True).exists():
            raise serializers.ValidationError('Produit introuvable.')
        return value

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return WishlistItem.objects.get_or_create(**validated_data)[0]
