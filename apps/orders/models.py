from django.db import models


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    DELIVERY_CHOICES = [
        ('express', 'Express'),
        ('standard', 'Standard'),
        ('pickup', 'Point de retrait'),
    ]
    PAYMENT_CHOICES = [
        ('card', 'Carte'),
        ('transfer', 'Virement'),
        ('pod', 'Paiement à la livraison'),
    ]

    user = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='orders')
    address = models.ForeignKey('users.Address', on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    promo_code = models.CharField(max_length=50, blank=True)
    discount_amount = models.PositiveIntegerField(default=0)
    delivery_method = models.CharField(max_length=20, choices=DELIVERY_CHOICES, default='standard')
    shipping_cost = models.PositiveIntegerField(default=0)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='pod')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Order #{self.pk} — {self.user}'

    @property
    def subtotal(self):
        return sum(item.line_total for item in self.items.all())

    @property
    def total(self):
        return max(0, self.subtotal - self.discount_amount) + self.shipping_cost


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    variant = models.ForeignKey('products.ProductVariant', on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=255)
    unit_price = models.PositiveIntegerField()
    qty = models.PositiveSmallIntegerField(default=1)

    @property
    def line_total(self):
        return self.unit_price * self.qty
