from django.db import models, transaction
from django.db.models import F


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('confirmed', 'Confirmée'),
        ('shipped', 'Expédiée'),
        ('delivered', 'Livrée'),
        ('cancelled', 'Annulée'),
    ]
    NEXT_STATUS = {'pending': 'confirmed', 'confirmed': 'shipped', 'shipped': 'delivered'}
    CANCELLABLE = ('pending', 'confirmed')
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

    user = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='orders', verbose_name='client')
    address = models.ForeignKey('users.Address', on_delete=models.SET_NULL, null=True, verbose_name='adresse de livraison')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='statut')
    promo_code = models.CharField(max_length=50, blank=True, verbose_name='code promo')
    discount_amount = models.PositiveIntegerField(default=0, verbose_name='réduction')
    delivery_method = models.CharField(max_length=20, choices=DELIVERY_CHOICES, default='standard', verbose_name='livraison')
    shipping_cost = models.PositiveIntegerField(default=0, verbose_name='frais de livraison')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='pod', verbose_name='paiement')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='créée le')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='modifiée le')

    class Meta:
        verbose_name = 'commande'
        verbose_name_plural = 'commandes'

    def __str__(self):
        return f'Commande #{self.pk}'

    @property
    def can_cancel(self):
        return self.status in self.CANCELLABLE

    @transaction.atomic
    def advance(self):
        """Passe au statut suivant (pending → confirmed → shipped → delivered). Retourne False si impossible."""
        order = Order.objects.select_for_update().get(pk=self.pk)
        next_status = self.NEXT_STATUS.get(order.status)
        if not next_status:
            return False
        order.status = self.status = next_status
        order.save(update_fields=['status', 'updated_at'])
        return True

    @transaction.atomic
    def cancel(self):
        """Annule la commande et restitue le stock. Retourne False si elle n'est plus annulable."""
        from apps.products.models import ProductVariant

        order = Order.objects.select_for_update().get(pk=self.pk)
        if not order.can_cancel:
            return False
        for item in order.items.exclude(variant=None):
            ProductVariant.objects.filter(pk=item.variant_id).update(stock=F('stock') + item.qty)
        order.status = self.status = 'cancelled'
        order.save(update_fields=['status', 'updated_at'])
        return True

    @property
    def subtotal(self):
        return sum(item.line_total for item in self.items.all())

    @property
    def total(self):
        return max(0, self.subtotal - self.discount_amount) + self.shipping_cost


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='commande')
    variant = models.ForeignKey('products.ProductVariant', on_delete=models.SET_NULL, null=True, verbose_name='variante')
    product_name = models.CharField(max_length=255, verbose_name='produit')
    unit_price = models.PositiveIntegerField(verbose_name='prix unitaire')
    qty = models.PositiveSmallIntegerField(default=1, verbose_name='quantité')

    class Meta:
        verbose_name = 'article'
        verbose_name_plural = 'articles'

    @property
    def line_total(self):
        return self.unit_price * self.qty
