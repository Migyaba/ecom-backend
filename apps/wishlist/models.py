from django.db import models


class WishlistItem(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='wishlist', verbose_name='utilisateur')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, verbose_name='produit')
    added_at = models.DateTimeField(auto_now_add=True, verbose_name='ajouté le')

    class Meta:
        verbose_name = 'favori'
        verbose_name_plural = 'favoris'
        unique_together = ('user', 'product')

    def __str__(self):
        return f'{self.user} → {self.product.name}'
