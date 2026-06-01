from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import (
    extend_schema, extend_schema_view, OpenApiExample, OpenApiResponse, OpenApiParameter
)
from drf_spectacular.types import OpenApiTypes

_ID_PARAM = OpenApiParameter('id', OpenApiTypes.INT, OpenApiParameter.PATH, description='Identifiant unique de la commande.')
from .models import Order
from .serializers import OrderSerializer, CreateOrderSerializer


@extend_schema(tags=['Orders'])
@extend_schema_view(
    list=extend_schema(
        summary='Lister mes commandes',
        description=(
            'Retourne l\'historique paginé des commandes de l\'utilisateur connecté, '
            'triées de la plus récente à la plus ancienne.\n\n'
            'Chaque commande inclut ses articles (`items`), son sous-total et son total après réduction.\n\n'
            '**Authentification requise.**'
        ),
        responses={200: OrderSerializer(many=True)},
    ),
    create=extend_schema(
        summary='Passer une commande',
        description=(
            'Crée une nouvelle commande à partir d\'un panier (liste de variantes + quantités).\n\n'
            '**Corps de la requête :**\n'
            '- `address_id` : ID d\'une adresse de livraison appartenant à l\'utilisateur connecté.\n'
            '- `items` : tableau d\'objets `{ variant_id, qty }` — au moins un article requis.\n\n'
            'Le statut initial de la commande est `pending`.\n'
            'Les prix unitaires sont snapshottés au moment de la commande '
            '(ils ne changeront pas si le produit est modifié plus tard).\n\n'
            '**Authentification requise.**'
        ),
        request=CreateOrderSerializer,
        responses={
            201: OrderSerializer,
            400: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
        },
        examples=[
            OpenApiExample(
                'Commande simple',
                value={
                    'address_id': 3,
                    'items': [
                        {'variant_id': 12, 'qty': 2},
                        {'variant_id': 7, 'qty': 1},
                    ],
                },
                request_only=True,
            ),
        ],
    ),
    retrieve=extend_schema(
        summary='Détail d\'une commande',
        description=(
            'Retourne le détail complet d\'une commande : statut, articles, '
            'adresse de livraison, total et réduction éventuelle.\n\n'
            '**Authentification requise.** Vous ne pouvez consulter que vos propres commandes.'
        ),
        parameters=[_ID_PARAM],
        responses={200: OrderSerializer},
    ),
)
class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = (permissions.IsAuthenticated,)
    http_method_names = ('get', 'post', 'head', 'options')

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items').order_by('-created_at')

    def create(self, request, *args, **kwargs):
        serializer = CreateOrderSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary='Annuler une commande',
        description=(
            'Annule une commande dont le statut est `pending` ou `confirmed`.\n\n'
            'Une commande déjà `shipped`, `delivered` ou `cancelled` **ne peut plus être annulée** '
            '— une erreur 400 est retournée dans ce cas.\n\n'
            '**Authentification requise.**'
        ),
        parameters=[_ID_PARAM],
        request=None,
        responses={
            200: OrderSerializer,
            400: OpenApiResponse(
                description='La commande ne peut plus être annulée (statut incompatible).',
                response=OpenApiTypes.OBJECT,
            ),
            404: OpenApiResponse(description='Commande introuvable.', response=OpenApiTypes.OBJECT),
        },
    )
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        order = self.get_object()
        if order.status not in ('pending', 'confirmed'):
            return Response({'detail': 'Cette commande ne peut plus être annulée.'}, status=status.HTTP_400_BAD_REQUEST)
        order.status = 'cancelled'
        order.save()
        return Response(OrderSerializer(order).data)
