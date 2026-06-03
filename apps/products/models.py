from django.db import models


class Category(models.Model):
    TONE_CHOICES = [
        ('indigo', 'Indigo'), ('bone', 'Bone'), ('brass', 'Brass'),
        ('sand', 'Sand'), ('ink', 'Ink'), ('rust', 'Rust'),
        ('cream', 'Cream'), ('sage', 'Sage'), ('ochre', 'Ochre'),
    ]

    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='children')
    eyebrow = models.CharField(max_length=60, blank=True, help_text='Petit label affiché au-dessus du titre (ex: Pour Elle)')
    tone = models.CharField(max_length=20, choices=TONE_CHOICES, default='sand', help_text='Couleur de fond du tile catégorie')
    cover_url = models.URLField(blank=True, help_text='Image de couverture par défaut (URL externe, Unsplash…)')

    class Meta:
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name


class Product(models.Model):
    BADGE_CHOICES = [('new', 'New'), ('sale', 'Sale')]

    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    price = models.PositiveIntegerField(help_text='Prix en FCFA (XOF)')
    original_price = models.PositiveIntegerField(null=True, blank=True)
    badge = models.CharField(max_length=10, choices=BADGE_CHOICES, blank=True)
    sale_ends_at = models.DateTimeField(null=True, blank=True, help_text='Date de fin de la promotion (null = pas de limite)')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def is_on_sale(self):
        return self.badge == 'sale' and self.original_price is not None


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/', blank=True)
    image_url = models.URLField(blank=True, help_text='URL externe (Unsplash, CDN…) quand aucun fichier uploadé')
    order = models.PositiveSmallIntegerField(default=0)
    is_cover = models.BooleanField(default=False)

    class Meta:
        ordering = ['order']


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    size = models.CharField(max_length=20, blank=True)
    color = models.CharField(max_length=30, blank=True)
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'{self.product.name} — {self.size} {self.color}'


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'user')


class Testimonial(models.Model):
    TONE_CHOICES = [
        ('cream', 'Cream'), ('bone', 'Bone'), ('sand', 'Sand'),
        ('indigo', 'Indigo'), ('rust', 'Rust'), ('ochre', 'Ochre'),
    ]
    name         = models.CharField(max_length=100)
    city         = models.CharField(max_length=100)
    text         = models.TextField()
    product_name = models.CharField(max_length=200, blank=True, help_text='Nom du produit acheté')
    rating       = models.PositiveSmallIntegerField(default=5)
    tone         = models.CharField(max_length=20, choices=TONE_CHOICES, default='cream')
    is_active    = models.BooleanField(default=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} ({self.city})'
