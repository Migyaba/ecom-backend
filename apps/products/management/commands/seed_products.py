"""
Management command : python manage.py seed_products
Crée les utilisateurs, boutiques et 10 produits de démonstration.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.users.models import User
from apps.stores.models import Store
from apps.products.models import Category, Product, ProductImage, ProductVariant


STORES = [
    {
        'email': 'sade@dinomarket.com', 'username': 'sade_atelier',
        'first_name': 'Sade', 'last_name': 'Atelier', 'password': 'demo1234',
        'store': {'name': 'Sade Atelier', 'slug': 'sade-atelier', 'city': 'Abidjan',
                  'description': 'Mode africaine contemporaine, pièces finies à la main.'},
    },
    {
        'email': 'maison@dinomarket.com', 'username': 'maison_kente',
        'first_name': 'Maison', 'last_name': 'Kente', 'password': 'demo1234',
        'store': {'name': 'Maison Kente', 'slug': 'maison-kente', 'city': 'Lagos',
                  'description': 'Créations kente et bogolan pour homme et femme.'},
    },
    {
        'email': 'bijoux@dinomarket.com', 'username': 'bijoux_afrik',
        'first_name': 'Bijoux', 'last_name': 'Afrik', 'password': 'demo1234',
        'store': {'name': 'Bijoux Afrik', 'slug': 'bijoux-afrik', 'city': 'Dakar',
                  'description': 'Bijoux artisanaux inspirés des traditions africaines.'},
    },
    {
        'email': 'casa@dinomarket.com', 'username': 'casa_dakar',
        'first_name': 'Casa', 'last_name': 'Dakar', 'password': 'demo1234',
        'store': {'name': 'Casa Dakar', 'slug': 'casa-dakar', 'city': 'Dakar',
                  'description': 'Décoration et objets artisanaux pour la maison africaine.'},
    },
    {
        'email': 'dapper@dinomarket.com', 'username': 'dapper_lagos',
        'first_name': 'Dapper', 'last_name': 'Lagos', 'password': 'demo1234',
        'store': {'name': 'Dapper Lagos', 'slug': 'dapper-lagos', 'city': 'Lagos',
                  'description': 'Mode homme et accessoires haut de gamme made in Africa.'},
    },
]

# Chaque entrée : (store_slug, category_slug, product_data, images_urls, variants)
PRODUCTS = [
    # ── Mode Femme ──────────────────────────────────────────────────────────
    (
        'sade-atelier', 'women',
        {
            'name': 'Robe Portefeuille Ankara',
            'slug': 'robe-portefeuille-ankara',
            'description': 'Robe portefeuille confectionnée à la main en tissu Ankara 100 % coton. Coupe fluide, boutonnage croisé, ceinture nouée. Disponible en rouge-ocre ou indigo.',
            'price': 45_000, 'badge': 'new',
        },
        [
            'https://images.unsplash.com/photo-1509631179647-0177331693ae?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1529139574466-a303027c1d8b?auto=format&fit=crop&w=800&q=80',
        ],
        [('XS', ''), ('S', ''), ('M', ''), ('L', ''), ('XL', '')],
    ),
    (
        'maison-kente', 'women',
        {
            'name': 'Ensemble Bogolan Femme',
            'slug': 'ensemble-bogolan-femme',
            'description': 'Ensemble deux pièces (top et jupe midi) en bogolan tissé main au Mali. Teintes naturelles terre, ocre et noir. Pièce unique, production limitée.',
            'price': 62_000, 'original_price': 85_000, 'badge': 'sale',
            'sale_ends_at': 'now+8h',
        },
        [
            'https://images.unsplash.com/photo-1483985988355-763728e1935b?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1469334031218-e382a71b716b?auto=format&fit=crop&w=800&q=80',
        ],
        [('S', ''), ('M', ''), ('L', '')],
    ),
    (
        'sade-atelier', 'women',
        {
            'name': 'Boubou Brodé Ivoire',
            'slug': 'boubou-brode-ivoire',
            'description': 'Grand boubou en mousseline ivoire, broderies dorées au col et aux manches. Idéal pour les cérémonies et événements formels.',
            'price': 38_500, 'badge': 'new',
        },
        [
            'https://images.unsplash.com/photo-1534030347209-467a5b0ad3e6?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1496747611176-843222e1e57c?auto=format&fit=crop&w=800&q=80',
        ],
        [('S', ''), ('M', ''), ('L', ''), ('XL', '')],
    ),
    # ── Mode Homme ──────────────────────────────────────────────────────────
    (
        'maison-kente', 'men',
        {
            'name': 'Agbada Contemporain',
            'slug': 'agbada-contemporain',
            'description': 'Agbada trois pièces revisité en brocart nigérian. Broderies main sur le devant, pantalon droit assorti, coupe moderne ajustée. Coloris champagne ou nuit.',
            'price': 75_000, 'badge': 'new',
        },
        [
            'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?auto=format&fit=crop&w=800&q=80',
        ],
        [('M', ''), ('L', ''), ('XL', ''), ('XXL', '')],
    ),
    (
        'dapper-lagos', 'men',
        {
            'name': 'Chemise Kente Slim',
            'slug': 'chemise-kente-slim',
            'description': 'Chemise coupe slim en tissu kente tissé main. Insertions de bandes colorées sur le col, les poignets et la boutonnière. Esprit contemporain et culturel.',
            'price': 28_000, 'original_price': 38_000, 'badge': 'sale',
            'sale_ends_at': 'now+4h',
        },
        [
            'https://images.unsplash.com/photo-1598033129183-c4f50c736f10?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1617137968427-85924c800a22?auto=format&fit=crop&w=800&q=80',
        ],
        [('S', ''), ('M', ''), ('L', ''), ('XL', '')],
    ),
    # ── Bijouterie ──────────────────────────────────────────────────────────
    (
        'bijoux-afrik', 'jewelry',
        {
            'name': 'Collier Perles d\'Or Akan',
            'slug': 'collier-perles-or-akan',
            'description': 'Collier ras-du-cou en perles d\'or et d\'ambre inspiré des parures royales Akan. Fermoir en laiton doré à l\'or fin. Longueur réglable.',
            'price': 32_000, 'badge': 'new',
        },
        [
            'https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?auto=format&fit=crop&w=800&q=80',
        ],
        [('Unique', '')],
    ),
    (
        'bijoux-afrik', 'jewelry',
        {
            'name': 'Boucles Masaï Laiton',
            'slug': 'boucles-masai-laiton',
            'description': 'Boucles d\'oreilles pendantes en laiton martelé à la main, perles de verre colorées d\'inspiration Masaï. Légères et audacieuses.',
            'price': 18_500, 'original_price': 24_000, 'badge': 'sale',
            'sale_ends_at': 'now+16h',
        },
        [
            'https://images.unsplash.com/photo-1535632787350-4e68ef0ac584?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1611085583191-a3b181a88401?auto=format&fit=crop&w=800&q=80',
        ],
        [('Unique', '')],
    ),
    # ── Maison & Déco ────────────────────────────────────────────────────────
    (
        'casa-dakar', 'home',
        {
            'name': 'Panier Osier Tressé',
            'slug': 'panier-osier-tresse',
            'description': 'Panier de rangement en osier tressé à la main par des artisanes sénégalaises. Taille moyenne, idéal pour le salon ou la chambre. Intérieur en coton naturel.',
            'price': 15_000, 'badge': 'new',
        },
        [
            'https://images.unsplash.com/photo-1586023492125-27b2c045efd7?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1555041469-a586c61ea9bc?auto=format&fit=crop&w=800&q=80',
        ],
        [('S', ''), ('M', ''), ('L', '')],
    ),
    (
        'casa-dakar', 'home',
        {
            'name': 'Coussin Batik Mali',
            'slug': 'coussin-batik-mali',
            'description': 'Coussin 45×45 cm en coton batik teint à la main au Mali. Motifs géométriques traditionnels en indigo et blanc. Housse amovible, garnissage inclus.',
            'price': 22_000, 'badge': 'new',
        },
        [
            'https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1540574163026-643ea20ade25?auto=format&fit=crop&w=800&q=80',
        ],
        [('45x45', 'Indigo'), ('45x45', 'Ocre')],
    ),
    # ── Horlogerie ──────────────────────────────────────────────────────────
    (
        'dapper-lagos', 'watches',
        {
            'name': 'Montre Acier Doré',
            'slug': 'montre-acier-dore',
            'description': 'Montre automatique boîtier acier doré 40 mm, cadran crème avec index dorés, bracelet cuir marron naturel tanné végétal. Mouvement japonais certifié.',
            'price': 125_000, 'original_price': 150_000, 'badge': 'sale',
            'sale_ends_at': 'now+36h',
        },
        [
            'https://images.unsplash.com/photo-1524592094714-0f0654e20314?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1523170335258-f5ed11844a49?auto=format&fit=crop&w=800&q=80',
        ],
        [('Unique', '')],
    ),
]


class Command(BaseCommand):
    help = 'Seed users, stores et 10 produits de démonstration'

    def _resolve_date(self, value):
        """Convertit 'now+Xh' en datetime absolu."""
        if not value or not isinstance(value, str):
            return value
        if value.startswith('now+') and value.endswith('h'):
            hours = int(value[4:-1])
            return timezone.now() + timedelta(hours=hours)
        return None

    def handle(self, *args, **options):
        self.stdout.write('Création des boutiques…')
        store_map = {}
        for data in STORES:
            user, _ = User.objects.get_or_create(
                email=data['email'],
                defaults={
                    'username': data['username'],
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                },
            )
            user.set_password(data['password'])
            user.save()

            store, created = Store.objects.get_or_create(
                slug=data['store']['slug'],
                defaults={**data['store'], 'owner': user},
            )
            store_map[store.slug] = store
            status = 'créée' if created else 'existante'
            self.stdout.write(f'  [{status}] {store.name}')

        self.stdout.write('Création / mise à jour des produits…')
        cats = {c.slug: c for c in Category.objects.all()}

        for store_slug, cat_slug, pdata, images, variants in PRODUCTS:
            store = store_map[store_slug]
            category = cats[cat_slug]

            # Résoudre sale_ends_at avant de passer au modèle
            pdata = dict(pdata)
            pdata['sale_ends_at'] = self._resolve_date(pdata.get('sale_ends_at'))

            product, created = Product.objects.get_or_create(
                slug=pdata['slug'],
                defaults={**pdata, 'store': store, 'category': category},
            )

            if not created and pdata.get('sale_ends_at'):
                product.sale_ends_at = pdata['sale_ends_at']
                product.save(update_fields=['sale_ends_at'])

            if created:
                for order, url in enumerate(images):
                    ProductImage.objects.create(
                        product=product,
                        image_url=url,
                        order=order,
                        is_cover=(order == 0),
                    )
                for size, color in variants:
                    ProductVariant.objects.create(
                        product=product, size=size, color=color, stock=10,
                    )

            status = 'créé' if created else 'mis à jour'
            ends = f' → expire {product.sale_ends_at.strftime("%H:%M")}' if product.sale_ends_at else ''
            self.stdout.write(f'  [{status}] {product.name}{ends}')

        self.stdout.write(self.style.SUCCESS(
            f'\nTerminé — {Product.objects.count()} produits en base.'
        ))
