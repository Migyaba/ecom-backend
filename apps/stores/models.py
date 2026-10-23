from django.db import models


class Store(models.Model):
    owner = models.OneToOneField('users.User', on_delete=models.CASCADE, related_name='store', verbose_name='propriétaire')
    name = models.CharField(max_length=150, verbose_name='nom')
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='stores/logos/', blank=True, null=True, verbose_name='logo')
    banner = models.ImageField(upload_to='stores/banners/', blank=True, null=True, verbose_name='bannière')
    city = models.CharField(max_length=100, blank=True, verbose_name='ville')
    country = models.CharField(max_length=100, default='Côte d\'Ivoire', verbose_name='pays')
    is_active = models.BooleanField(default=True, verbose_name='active')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='créée le')

    class Meta:
        verbose_name = 'boutique'
        verbose_name_plural = 'boutiques'

    def __str__(self):
        return self.name
