from django.conf import settings
from django.db import transaction
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes
from .models import Order, OrderItem
from apps.products.models import ProductVariant
from apps.users.models import Address

SHIPPING_COSTS = {'express': 3500, 'standard': 2500, 'pickup': 0}
FREE_STANDARD_SHIPPING_FROM = 50000


def compute_shipping(delivery_method, subtotal):
    if delivery_method == 'standard' and subtotal > FREE_STANDARD_SHIPPING_FROM:
        return 0
    return SHIPPING_COSTS[delivery_method]


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
    qty = serializers.IntegerField(min_value=1, max_value=99, default=1)


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    subtotal = serializers.IntegerField(read_only=True)
    total = serializers.IntegerField(read_only=True)

    class Meta:
        model = Order
        fields = (
            'id', 'status', 'address', 'promo_code', 'discount_amount',
            'delivery_method', 'shipping_cost', 'payment_method',
            'subtotal', 'total', 'items', 'created_at',
        )
        read_only_fields = fields


class CreateOrderSerializer(serializers.Serializer):
    address_id = serializers.IntegerField()
    items = OrderItemCreateSerializer(many=True)
    delivery_method = serializers.ChoiceField(choices=Order.DELIVERY_CHOICES, default='standard')
    payment_method = serializers.ChoiceField(choices=Order.PAYMENT_CHOICES, default='pod')
    promo_code = serializers.CharField(max_length=50, required=False, allow_blank=True, default='')

    def validate_address_id(self, value):
        if not Address.objects.filter(pk=value, user=self.context['request'].user).exists():
            raise serializers.ValidationError('Adresse de livraison introuvable.')
        return value

    def validate_promo_code(self, value):
        code = value.strip().upper()
        if code and code not in settings.PROMO_CODES:
            raise serializers.ValidationError('Code promo invalide.')
        return code

    def validate_items(self, items):
        if not items:
            raise serializers.ValidationError('La commande doit contenir au moins un article.')
        # Fusionne les lignes qui pointent sur la même variante
        merged = {}
        for item in items:
            merged[item['variant_id']] = merged.get(item['variant_id'], 0) + item['qty']
        return [{'variant_id': vid, 'qty': qty} for vid, qty in merged.items()]

    @transaction.atomic
    def create(self, validated_data):
        items = validated_data['items']
        variants = {
            v.pk: v
            for v in ProductVariant.objects.select_for_update().select_related('product').filter(
                pk__in=[i['variant_id'] for i in items], product__is_active=True,
            )
        }

        errors = []
        for item in items:
            variant = variants.get(item['variant_id'])
            if variant is None:
                errors.append(f"L'article {item['variant_id']} n'est plus disponible.")
            elif variant.stock < item['qty']:
                errors.append(f'Stock insuffisant pour « {variant.product.name} » ({variant.stock} restant).')
        if errors:
            raise serializers.ValidationError({'items': errors})

        subtotal = sum(variants[i['variant_id']].product.price * i['qty'] for i in items)
        promo_code = validated_data['promo_code']
        discount = subtotal * settings.PROMO_CODES[promo_code] // 100 if promo_code else 0
        delivery_method = validated_data['delivery_method']

        order = Order.objects.create(
            user=self.context['request'].user,
            address_id=validated_data['address_id'],
            promo_code=promo_code,
            discount_amount=discount,
            delivery_method=delivery_method,
            shipping_cost=compute_shipping(delivery_method, subtotal),
            payment_method=validated_data['payment_method'],
        )
        for item in items:
            variant = variants[item['variant_id']]
            OrderItem.objects.create(
                order=order,
                variant=variant,
                product_name=variant.product.name,
                unit_price=variant.product.price,
                qty=item['qty'],
            )
            variant.stock -= item['qty']
        ProductVariant.objects.bulk_update(variants.values(), ['stock'])
        return order
