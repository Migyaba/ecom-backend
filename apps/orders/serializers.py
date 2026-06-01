from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes
from .models import Order, OrderItem
from apps.products.models import ProductVariant


class OrderItemSerializer(serializers.ModelSerializer):
    line_total = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ('id', 'product_name', 'unit_price', 'qty', 'line_total')
        read_only_fields = ('id', 'line_total')

    @extend_schema_field(OpenApiTypes.INT)
    def get_line_total(self, obj):
        return obj.line_total


class OrderItemCreateSerializer(serializers.Serializer):
    variant_id = serializers.IntegerField()
    qty = serializers.IntegerField(min_value=1, default=1)


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    subtotal = serializers.IntegerField(read_only=True)
    total = serializers.IntegerField(read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'status', 'address', 'promo_code', 'discount_amount', 'subtotal', 'total', 'items', 'created_at')
        read_only_fields = ('id', 'status', 'discount_amount', 'subtotal', 'total', 'created_at')


class CreateOrderSerializer(serializers.Serializer):
    address_id = serializers.IntegerField()
    items = OrderItemCreateSerializer(many=True)

    def validate_items(self, items):
        if not items:
            raise serializers.ValidationError('La commande doit contenir au moins un article.')
        return items

    def create(self, validated_data):
        user = self.context['request'].user
        order = Order.objects.create(
            user=user,
            address_id=validated_data['address_id'],
        )
        for item_data in validated_data['items']:
            variant = ProductVariant.objects.select_related('product').get(pk=item_data['variant_id'])
            OrderItem.objects.create(
                order=order,
                variant=variant,
                product_name=variant.product.name,
                unit_price=variant.product.price,
                qty=item_data['qty'],
            )
        return order
