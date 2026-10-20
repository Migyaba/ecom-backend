from rest_framework import viewsets, permissions
from drf_spectacular.utils import (
    extend_schema, extend_schema_view, OpenApiExample, OpenApiParameter
)
from drf_spectacular.types import OpenApiTypes

_ID_PARAM = OpenApiParameter('id', OpenApiTypes.INT, OpenApiParameter.PATH, description='Identifiant unique de l\'item wishlist.')
from .models import WishlistItem
from .serializers import WishlistItemSerializer


@extend_schema(tags=['Wishlist'])
@extend_schema_view(
    list=extend_schema(
        summary='Voir ma liste de souhaits',
        description=(
            'Retourne tous les produits enregistrés dans la liste de souhaits '
            'de l\'utilisateur connecté.\n\n'
            'Chaque item inclut le produit complet (image de couverture, prix, badge).\n\n'
            '**Authentification requise.**'
        ),
        responses={200: WishlistItemSerializer(many=True)},
    ),
    create=extend_schema(
        summary='Ajouter un produit à la liste de souhaits',
        description=(
            'Ajoute un produit à la liste de souhaits via son `product_id`.\n\n'
            '**Idempotent :** si le produit est déjà dans la liste, '
            'l\'opération retourne l\'item existant sans créer de doublon.\n\n'
            '**Authentification requise.**'
        ),
        request=WishlistItemSerializer,
        responses={201: WishlistItemSerializer},
        examples=[
            OpenApiExample(
                'Ajouter un produit',
                value={'product_id': 42},
                request_only=True,
            ),
        ],
    ),
    retrieve=extend_schema(
        summary='Détail d\'un item de la liste de souhaits',
        description=(
            'Retourne un item spécifique de la liste de souhaits avec le détail du produit.\n\n'
            '**Authentification requise.**'
        ),
        parameters=[_ID_PARAM],
        responses={200: WishlistItemSerializer},
    ),
    destroy=extend_schema(
        summary='Retirer un produit de la liste de souhaits',
        description=(
            'Supprime un item de la liste de souhaits.\n\n'
            'Le produit lui-même n\'est pas affecté.\n\n'
            '**Authentification requise.**'
        ),
        parameters=[_ID_PARAM],
        responses={204: None},
    ),
)
class WishlistViewSet(viewsets.ModelViewSet):
    serializer_class = WishlistItemSerializer
    permission_classes = (permissions.IsAuthenticated,)
    http_method_names = ('get', 'post', 'delete', 'head', 'options')

    def get_queryset(self):
        return WishlistItem.objects.filter(user=self.request.user).select_related('product__store', 'product__category').prefetch_related('product__images', 'product__variants')
