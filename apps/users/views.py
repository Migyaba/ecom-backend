from rest_framework import generics, viewsets, permissions
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

_ID_PARAM = OpenApiParameter('id', OpenApiTypes.INT, OpenApiParameter.PATH, description='Identifiant unique.')
from .models import User, Address
from .serializers import RegisterSerializer, UserSerializer, AddressSerializer


@extend_schema(
    tags=['Users'],
    summary='Créer un compte utilisateur',
    description=(
        'Enregistre un nouvel utilisateur. Aucun token n\'est requis.\n\n'
        '**Règles de validation :**\n'
        '- `email` doit être unique sur la plateforme.\n'
        '- `password` et `password2` doivent être identiques.\n'
        '- Le mot de passe est soumis aux validateurs Django (longueur min. 8 caractères, '
        'pas uniquement numérique, etc.).\n\n'
        '**Après inscription**, obtenez votre token via `POST /api/auth/token/`.'
    ),
    request=RegisterSerializer,
    responses={201: UserSerializer},
    examples=[
        OpenApiExample(
            'Exemple d\'inscription',
            value={
                'email': 'fatou@example.com',
                'username': 'fatou22',
                'first_name': 'Fatou',
                'last_name': 'Diallo',
                'password': 'monMotDePasse123',
                'password2': 'monMotDePasse123',
            },
            request_only=True,
        ),
    ],
)
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = (permissions.AllowAny,)


@extend_schema(
    tags=['Users'],
)
@extend_schema_view(
    get=extend_schema(
        summary='Obtenir mon profil',
        description=(
            'Retourne les informations du compte authentifié : identifiants, téléphone et avatar.\n\n'
            'Champs **en lecture seule** : `id`, `email`.'
        ),
        responses={200: UserSerializer},
    ),
    put=extend_schema(
        summary='Mettre à jour mon profil (remplacement complet)',
        description=(
            'Remplace l\'intégralité du profil. Tous les champs non read-only sont requis.\n\n'
            'Pour une mise à jour partielle, préférez `PATCH /api/users/me/`.'
        ),
        request=UserSerializer,
        responses={200: UserSerializer},
    ),
    patch=extend_schema(
        summary='Mettre à jour mon profil (partiel)',
        description=(
            'Met à jour un ou plusieurs champs du profil sans toucher aux autres.\n\n'
            'Utile pour changer uniquement l\'avatar ou le numéro de téléphone.\n\n'
            '**Champs modifiables :** `username`, `first_name`, `last_name`, `phone`, `avatar`.'
        ),
        request=UserSerializer,
        responses={200: UserSerializer},
        examples=[
            OpenApiExample(
                'Mise à jour du téléphone',
                value={'phone': '+2348012345678'},
                request_only=True,
            ),
        ],
    ),
)
class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user


@extend_schema(tags=['Users'])
@extend_schema_view(
    list=extend_schema(
        summary='Lister mes adresses',
        description='Retourne toutes les adresses de livraison associées au compte connecté.',
        responses={200: AddressSerializer(many=True)},
    ),
    create=extend_schema(
        summary='Ajouter une adresse',
        description=(
            'Crée une nouvelle adresse de livraison pour l\'utilisateur connecté.\n\n'
            'Si `is_default` est `true`, toutes les autres adresses de l\'utilisateur '
            'sont automatiquement passées à `is_default: false`.'
        ),
        request=AddressSerializer,
        responses={201: AddressSerializer},
        examples=[
            OpenApiExample(
                'Nouvelle adresse domicile',
                value={
                    'label': 'Maison',
                    'full_name': 'Fatou Diallo',
                    'line1': '12 rue des Palmiers',
                    'line2': 'Appt 3B',
                    'city': 'Abidjan',
                    'state': 'Abidjan',
                    'country': 'Côte d\'Ivoire',
                    'is_default': True,
                },
                request_only=True,
            ),
        ],
    ),
    retrieve=extend_schema(
        summary='Détail d\'une adresse',
        description='Retourne une adresse spécifique de l\'utilisateur connecté.',
        parameters=[_ID_PARAM],
        responses={200: AddressSerializer},
    ),
    update=extend_schema(
        summary='Modifier une adresse (remplacement complet)',
        description='Remplace l\'intégralité d\'une adresse existante.',
        parameters=[_ID_PARAM],
        request=AddressSerializer,
        responses={200: AddressSerializer},
    ),
    partial_update=extend_schema(
        summary='Modifier une adresse (partiel)',
        description=(
            'Met à jour un ou plusieurs champs d\'une adresse.\n\n'
            'Si `is_default` passe à `true`, les autres adresses sont automatiquement désactivées.'
        ),
        parameters=[_ID_PARAM],
        request=AddressSerializer,
        responses={200: AddressSerializer},
    ),
    destroy=extend_schema(
        summary='Supprimer une adresse',
        description='Supprime définitivement une adresse de livraison.',
        parameters=[_ID_PARAM],
        responses={204: None},
    ),
)
class AddressViewSet(viewsets.ModelViewSet):
    serializer_class = AddressSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)
