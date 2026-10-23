from django.db import models


class Category(models.Model):
    TONE_CHOICES = [
        ('indigo', 'Indigo'), ('bone', 'Bone'), ('brass', 'Brass'),
        ('sand', 'Sand'), ('ink', 'Ink'), ('rust', 'Rust'),
        ('cream', 'Cream'), ('sage', 'Sage'), ('ochre', 'Ochre'),
    ]

    name = models.CharField(max_length=100, verbose_name='nom')
    slug = models.SlugField(unique=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='children', verbose_name='catégorie parente')
    eyebrow = models.CharField(max_length=60, blank=True, help_text='Petit label affiché au-dessus du titre (ex: Pour Elle)', verbose_name='sur-titre')
    tone = models.CharField(max_length=20, choices=TONE_CHOICES, default='sand', help_text='Couleur de fond du tile catégorie', verbose_name='couleur')
    cover_url = models.URLField(blank=True, help_text='Image de couverture par défaut (URL externe, Unsplash…)', verbose_name='image de couverture')

    class Meta:
        verbose_name = 'catégorie'
        verbose_name_plural = 'catégories'

    def __str__(self):
        return self.name


class Product(models.Model):
    BADGE_CHOICES = [('new', 'Nouveau'), ('sale', 'Promo')]

    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE, related_name='products', verbose_name='boutique')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products', verbose_name='catégorie')
    name = models.CharField(max_length=255, verbose_name='nom')
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    price = models.PositiveIntegerField(help_text='Prix en FCFA (XOF)', verbose_name='prix')
    original_price = models.PositiveIntegerField(null=True, blank=True, verbose_name='prix barré')
    badge = models.CharField(max_length=10, choices=BADGE_CHOICES, blank=True)
    sale_ends_at = models.DateTimeField(null=True, blank=True, help_text='Date de fin de la promotion (null = pas de limite)', verbose_name='fin de la promo')
    is_active = models.BooleanField(default=True, verbose_name='en ligne')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='créé le')

    class Meta:
        verbose_name = 'produit'
        verbose_name_plural = 'produits'

    def __str__(self):
        return self.name

    @property
    def is_on_sale(self):
        return self.badge == 'sale' and self.original_price is not None


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', verbose_name='produit')
    image = models.ImageField(upload_to='products/', blank=True, verbose_name='fichier')
    image_url = models.URLField(blank=True, help_text='URL externe (Unsplash, CDN…) quand aucun fichier uploadé', verbose_name="URL de l'image")
    order = models.PositiveSmallIntegerField(default=0, verbose_name='ordre')
    is_cover = models.BooleanField(default=False, verbose_name='couverture')

    class Meta:
        verbose_name = 'image'
        verbose_name_plural = 'images'
        ordering = ['order']


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants', verbose_name='produit')
    size = models.CharField(max_length=20, blank=True, verbose_name='taille')
    color = models.CharField(max_length=30, blank=True, verbose_name='couleur')
    stock = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'variante'
        verbose_name_plural = 'variantes'

    def __str__(self):
        return f'{self.product.name} — {self.size} {self.color}'


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews', verbose_name='produit')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, verbose_name='auteur')
    rating = models.PositiveSmallIntegerField(verbose_name='note')
    body = models.TextField(verbose_name='avis')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='publié le')

    class Meta:
        verbose_name = 'avis client'
        verbose_name_plural = 'avis clients'
        unique_together = ('product', 'user')


class Testimonial(models.Model):
    TONE_CHOICES = [
        ('cream', 'Cream'), ('bone', 'Bone'), ('sand', 'Sand'),
        ('indigo', 'Indigo'), ('rust', 'Rust'), ('ochre', 'Ochre'),
    ]
    name         = models.CharField(max_length=100, verbose_name='nom')
    city         = models.CharField(max_length=100, verbose_name='ville')
    text         = models.TextField(verbose_name='texte')
    product_name = models.CharField(max_length=200, blank=True, help_text='Nom du produit acheté', verbose_name='produit acheté')
    rating       = models.PositiveSmallIntegerField(default=5, verbose_name='note')
    tone         = models.CharField(max_length=20, choices=TONE_CHOICES, default='cream', verbose_name='couleur')
    is_active    = models.BooleanField(default=True, verbose_name='affiché')
    created_at   = models.DateTimeField(auto_now_add=True, verbose_name='créé le')

    class Meta:
        verbose_name = 'témoignage'
        verbose_name_plural = 'témoignages'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} ({self.city})'
