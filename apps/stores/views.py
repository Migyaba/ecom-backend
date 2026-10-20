from rest_framework import viewsets, permissions
from django.utils.text import slugify
from drf_spectacular.utils import (
    extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
)
from drf_spectacular.types import OpenApiTypes
from .models import Store
from .serializers import StoreSerializer


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user


@extend_schema(tags=['Stores'])
@extend_schema_view(
    list=extend_schema(
        summary='Lister les boutiques actives',
        description=(
            'Retourne la liste paginée de toutes les boutiques actives sur la plateforme.\n\n'
            '**Accès public** — aucun token requis.'
        ),
        responses={200: StoreSerializer(many=True)},
    ),
    create=extend_schema(
        summary='Créer ma boutique',
        description=(
            'Crée une boutique rattachée au compte connecté.\n\n'
            '**Règles :**\n'
            '- Un utilisateur ne peut posséder qu\'**une seule boutique** (relation OneToOne).\n'
            '- Le `slug` est généré automatiquement à partir du nom (vous n\'avez pas à le fournir).\n'
            '- Les champs `logo` et `banner` acceptent des fichiers image (multipart/form-data).\n\n'
            '**Authentification requise.**'
        ),
        request=StoreSerializer,
        responses={201: StoreSerializer},
        examples=[
            OpenApiExample(
                'Nouvelle boutique',
                value={
                    'name': 'Sadé Atelier',
                    'description': 'Pagnes et tenues sur mesure, cousus main à Abidjan.',
                    'city': 'Abidjan',
                    'country': 'Côte d\'Ivoire',
                },
                request_only=True,
            ),
        ],
    ),
    retrieve=extend_schema(
        summary='Détail d\'une boutique',
        description=(
            'Retourne le profil complet d\'une boutique identifiée par son **slug**.\n\n'
            '**Accès public** — aucun token requis.'
        ),
        responses={200: StoreSerializer},
        parameters=[
            OpenApiParameter(
                'slug', OpenApiTypes.STR, OpenApiParameter.PATH,
                description='Slug unique de la boutique (ex. `sade-atelier`).',
            ),
        ],
    ),
    update=extend_schema(
        summary='Modifier ma boutique (remplacement complet)',
        description=(
            'Remplace toutes les informations de la boutique.\n\n'
            '**Authentification requise.** Seul le propriétaire peut modifier sa boutique.'
        ),
        request=StoreSerializer,
        responses={200: StoreSerializer},
    ),
    partial_update=extend_schema(
        summary='Modifier ma boutique (partiel)',
        description=(
            'Met à jour un ou plusieurs champs de la boutique.\n\n'
            'Utile pour changer uniquement le logo ou la description.\n\n'
            '**Authentification requise.** Seul le propriétaire peut modifier sa boutique.'
        ),
        request=StoreSerializer,
        responses={200: StoreSerializer},
    ),
    destroy=extend_schema(
        summary='Supprimer ma boutique',
        description=(
            'Supprime définitivement la boutique et tous ses produits associés.\n\n'
            '**Attention : opération irréversible.**\n\n'
            '**Authentification requise.** Seul le propriétaire peut supprimer sa boutique.'
        ),
        responses={204: None},
    ),
)
class StoreViewSet(viewsets.ModelViewSet):
    queryset = Store.objects.filter(is_active=True)
    serializer_class = StoreSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly)
    lookup_field = 'slug'

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user, slug=unique_slug(serializer.validated_data['name']))


def unique_slug(name):
    base = slugify(name) or 'boutique'
    slug, n = base, 2
    while Store.objects.filter(slug=slug).exists():
        slug, n = f'{base}-{n}', n + 1
    return slug
