from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, verbose_name='téléphone')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='avatar')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses', verbose_name='utilisateur')
    label = models.CharField(max_length=50, default='Home', verbose_name='libellé')
    full_name = models.CharField(max_length=150, verbose_name='nom complet')
    line1 = models.CharField(max_length=255, verbose_name='adresse')
    line2 = models.CharField(max_length=255, blank=True, verbose_name='complément')
    city = models.CharField(max_length=100, verbose_name='ville')
    state = models.CharField(max_length=100, verbose_name='région')
    country = models.CharField(max_length=100, default='Côte d\'Ivoire', verbose_name='pays')
    is_default = models.BooleanField(default=False, verbose_name='par défaut')

    class Meta:
        verbose_name = 'adresse'
        verbose_name_plural = 'adresses'

    def __str__(self):
        return f'{self.label} — {self.user.email}'
