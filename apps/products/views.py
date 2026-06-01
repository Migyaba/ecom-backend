from rest_framework import viewsets, generics, permissions, filters
from drf_spectacular.utils import (
    extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
)
from drf_spectacular.types import OpenApiTypes
from .models import Category, Product, Review
from .serializers import (
    CategorySerializer, ProductListSerializer,
    ProductDetailSerializer, ReviewSerializer,
)


@extend_schema(tags=['Products'])
@extend_schema_view(
    list=extend_schema(
        summary='Lister toutes les catégories',
        description=(
            'Retourne la liste complète des catégories de produits.\n\n'
            'Les catégories peuvent être hiérarchiques : le champ `parent` contient '
            'l\'ID de la catégorie parente (ou `null` pour les catégories racines).\n\n'
            '**Accès public** — aucun token requis.'
        ),
        responses={200: CategorySerializer(many=True)},
    ),
    retrieve=extend_schema(
        summary='Détail d\'une catégorie',
        description=(
            'Retourne une catégorie par son **slug** (ex. `dinosaures-carnivores`).\n\n'
            '**Accès public** — aucun token requis.'
        ),
        responses={200: CategorySerializer},
        parameters=[
            OpenApiParameter(
                'slug', OpenApiTypes.STR, OpenApiParameter.PATH,
                description='Slug unique de la catégorie (ex. `dinosaures-carnivores`).',
            ),
        ],
    ),
)
class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (permissions.AllowAny,)
    lookup_field = 'slug'


@extend_schema(tags=['Products'])
@extend_schema_view(
    list=extend_schema(
        summary='Lister les produits',
        description=(
            'Retourne la liste paginée des produits actifs avec leurs informations essentielles '
            '(image de couverture, prix, badge promo).\n\n'
            '**Filtres disponibles :**\n'
            '| Paramètre | Type | Description |\n'
            '|-----------|------|-------------|\n'
            '| `category` | string | Slug de la catégorie |\n'
            '| `badge` | string | `new` ou `sale` |\n'
            '| `store` | string | Slug de la boutique |\n'
            '| `search` | string | Recherche dans le nom, la boutique, la catégorie |\n'
            '| `ordering` | string | `price`, `-price`, `created_at`, `-created_at` |\n\n'
            '**Accès public** — aucun token requis.'
        ),
        responses={200: ProductListSerializer(many=True)},
        parameters=[
            OpenApiParameter(
                'category', OpenApiTypes.STR, OpenApiParameter.QUERY,
                description='Filtrer par slug de catégorie (ex. `figurines`).',
                required=False,
            ),
            OpenApiParameter(
                'badge', OpenApiTypes.STR, OpenApiParameter.QUERY,
                description='Filtrer par badge : `new` (nouveautés) ou `sale` (promotions).',
                required=False,
                enum=['new', 'sale'],
            ),
            OpenApiParameter(
                'store', OpenApiTypes.STR, OpenApiParameter.QUERY,
                description='Filtrer par slug de boutique (ex. `dino-shop-lagos`).',
                required=False,
            ),
            OpenApiParameter(
                'search', OpenApiTypes.STR, OpenApiParameter.QUERY,
                description='Recherche textuelle sur le nom du produit, de la boutique ou de la catégorie.',
                required=False,
            ),
            OpenApiParameter(
                'ordering', OpenApiTypes.STR, OpenApiParameter.QUERY,
                description='Trier les résultats. Valeurs : `price`, `-price`, `created_at`, `-created_at`.',
                required=False,
            ),
        ],
    ),
    retrieve=extend_schema(
        summary='Fiche produit complète',
        description=(
            'Retourne le détail complet d\'un produit par son **slug** :\n'
            '- Toutes les images (galerie)\n'
            '- Les variantes disponibles (taille, couleur, stock)\n'
            '- Les avis clients avec note moyenne\n'
            '- Indicateur de promotion (`is_on_sale`)\n\n'
            '**Accès public** — aucun token requis.'
        ),
        responses={200: ProductDetailSerializer},
        parameters=[
            OpenApiParameter(
                'slug', OpenApiTypes.STR, OpenApiParameter.PATH,
                description='Slug unique du produit (ex. `t-rex-en-peluche-xl`).',
            ),
        ],
    ),
)
class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.filter(is_active=True).select_related('store', 'category').prefetch_related('images')
    permission_classes = (permissions.AllowAny,)
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('name', 'store__name', 'category__name')
    ordering_fields = ('price', 'created_at')
    ordering = ('-created_at',)
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProductDetailSerializer
        return ProductListSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        cat = self.request.query_params.get('category')
        badge = self.request.query_params.get('badge')
        store = self.request.query_params.get('store')
        if cat:
            qs = qs.filter(category__slug=cat)
        if badge:
            qs = qs.filter(badge=badge)
        if store:
            qs = qs.filter(store__slug=store)
        return qs


@extend_schema(
    tags=['Products'],
    summary='Poster un avis sur un produit',
    description=(
        'Crée un avis client sur un produit identifié par son **slug**.\n\n'
        '**Contraintes :**\n'
        '- Un utilisateur ne peut laisser **qu\'un seul avis** par produit.\n'
        '- La note (`rating`) doit être un entier positif.\n'
        '- L\'auteur est automatiquement défini à partir du token JWT.\n\n'
        '**Authentification requise.**'
    ),
    request=ReviewSerializer,
    responses={
        201: ReviewSerializer,
        400: OpenApiTypes.OBJECT,
        401: OpenApiTypes.OBJECT,
    },
    parameters=[
        OpenApiParameter(
            'slug', OpenApiTypes.STR, OpenApiParameter.PATH,
            description='Slug du produit sur lequel poster l\'avis.',
        ),
    ],
    examples=[
        OpenApiExample(
            'Avis 5 étoiles',
            value={'rating': 5, 'body': 'Superbe produit, livraison rapide !'},
            request_only=True,
        ),
        OpenApiExample(
            'Avis négatif',
            value={'rating': 2, 'body': 'Qualité décevante par rapport aux photos.'},
            request_only=True,
        ),
    ],
)
class ReviewCreateView(generics.CreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['product'] = generics.get_object_or_404(Product, slug=self.kwargs['slug'])
        return ctx
