from django.db import models


class Store(models.Model):
    owner = models.OneToOneField('users.User', on_delete=models.CASCADE, related_name='store')
    name = models.CharField(max_length=150)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='stores/logos/', blank=True, null=True)
    banner = models.ImageField(upload_to='stores/banners/', blank=True, null=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, default='Côte d\'Ivoire')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
