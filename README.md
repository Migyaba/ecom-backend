# DinoMarket — Backend API

API REST du marketplace e-commerce multi-vendeurs DinoMarket, construite avec **Django 6** et **Django REST Framework**.

---

## Table des matières

1. [Stack technique](#stack-technique)
2. [Architecture du projet](#architecture-du-projet)
3. [Prérequis](#prérequis)
4. [Installation et démarrage](#installation-et-démarrage)
5. [Variables d'environnement](#variables-denvironnement)
6. [Base de données](#base-de-données)
7. [Authentification](#authentification)
8. [Référence des endpoints](#référence-des-endpoints)
   - [Auth](#auth)
   - [Users](#users)
   - [Stores](#stores)
   - [Products](#products)
   - [Orders](#orders)
   - [Wishlist](#wishlist)
9. [Pagination et filtres](#pagination-et-filtres)
10. [Gestion des fichiers media](#gestion-des-fichiers-media)
11. [Documentation Swagger](#documentation-swagger)
12. [Déploiement en production](#déploiement-en-production)
13. [Conventions](#conventions)

---

## Stack technique

| Composant | Technologie | Version |
|---|---|---|
| Framework web | Django | 6.0.5 |
| API REST | Django REST Framework | 3.17.1 |
| Authentification | Simple JWT | 5.5.1 |
| Documentation API | drf-spectacular (OpenAPI 3) | 0.28.0 |
| CORS | django-cors-headers | 4.9.0 |
| Images | Pillow | 12.2.0 |
| BDD (dev) | SQLite | — |
| BDD (prod) | MySQL (o2switch) | — |
| Hébergement | o2switch | — |

---

## Architecture du projet

```
backend/
├── config/
│   ├── settings/
│   │   ├── base.py          # Settings partagés
│   │   ├── development.py   # SQLite + CORS Vite/React
│   │   └── production.py    # MySQL + HTTPS + SMTP
│   ├── urls.py              # Routeur principal + docs Swagger
│   ├── wsgi.py
│   └── asgi.py
├── apps/
│   ├── users/               # Comptes, profils, adresses
│   ├── stores/              # Boutiques des vendeurs
│   ├── products/            # Catalogue, catégories, avis
│   ├── orders/              # Commandes
│   └── wishlist/            # Liste de souhaits
├── media/                   # Fichiers uploadés (avatars, produits, logos)
├── staticfiles/             # Fichiers statiques collectés
├── manage.py
├── requirements.txt
└── .env                     # Variables d'environnement (non versionné)
```

Chaque application Django (`apps/`) suit la structure standard :
`models.py` → `serializers.py` → `views.py` → `urls.py`

---

## Prérequis

- Python **3.12+**
- pip
- (Production uniquement) MySQL 8+ et un serveur SMTP

---

## Installation et démarrage

### 1. Cloner le dépôt

```bash
git clone <url-du-repo>
cd dinomarket/backend
```

### 2. Créer et activer l'environnement virtuel

```bash
python -m venv .venv
source .venv/bin/activate        # Linux / macOS
# .venv\Scripts\activate         # Windows
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Configurer les variables d'environnement

```bash
cp .env.example .env
# Éditer .env avec les valeurs réelles
```

### 5. Appliquer les migrations

```bash
python manage.py migrate
```

### 6. Créer un super-utilisateur (optionnel)

```bash
python manage.py createsuperuser
```

### 7. Lancer le serveur de développement

```bash
python manage.py runserver
```

Le serveur démarre sur `http://127.0.0.1:8000`.

> **Note :** Le projet utilise `config.settings.development` par défaut (SQLite, DEBUG=True, emails dans la console).
> Pour utiliser les settings de production : `DJANGO_SETTINGS_MODULE=config.settings.production python manage.py runserver`

---

## Variables d'environnement

Copier `.env.example` → `.env` et renseigner les valeurs.

| Variable | Obligatoire | Description |
|---|---|---|
| `SECRET_KEY` | Oui | Clé secrète Django (longue chaîne aléatoire en prod) |
| `ALLOWED_HOSTS` | Prod | Domaines autorisés, séparés par des virgules |
| `CORS_ALLOWED_ORIGINS` | Prod | Origines frontend autorisées |
| `DB_NAME` | Prod | Nom de la base MySQL |
| `DB_USER` | Prod | Utilisateur MySQL |
| `DB_PASSWORD` | Prod | Mot de passe MySQL |
| `DB_HOST` | Prod | Hôte MySQL (défaut : `localhost`) |
| `DB_PORT` | Prod | Port MySQL (défaut : `3306`) |
| `EMAIL_HOST` | Prod | Serveur SMTP (ex. `mail.o2switch.net`) |
| `EMAIL_PORT` | Prod | Port SMTP (ex. `587`) |
| `EMAIL_HOST_USER` | Prod | Adresse email SMTP |
| `EMAIL_HOST_PASSWORD` | Prod | Mot de passe SMTP |

---

## Base de données

### Développement — SQLite

Aucune configuration requise. Le fichier `db.sqlite3` est créé automatiquement à la racine du backend.

### Production — MySQL (o2switch)

La base est configurée via les variables d'environnement. Encoding `utf8mb4` forcé pour le support des caractères spéciaux.

### Migrations

```bash
# Appliquer toutes les migrations
python manage.py migrate

# Créer les migrations après modification d'un modèle
python manage.py makemigrations

# Voir l'état des migrations
python manage.py showmigrations
```

### Modèles de données

#### `users.User` (extension de AbstractUser)
| Champ | Type | Description |
|---|---|---|
| `email` | EmailField unique | Identifiant de connexion |
| `username` | CharField | Nom d'utilisateur |
| `first_name` / `last_name` | CharField | Prénom / Nom |
| `phone` | CharField | Numéro de téléphone |
| `avatar` | ImageField | Photo de profil |

#### `users.Address`
| Champ | Type | Description |
|---|---|---|
| `label` | CharField | Ex. "Maison", "Bureau" |
| `full_name` | CharField | Nom complet du destinataire |
| `line1` / `line2` | CharField | Lignes d'adresse |
| `city` / `state` / `country` | CharField | Localisation |
| `is_default` | BooleanField | Adresse principale |

#### `stores.Store`
| Champ | Type | Description |
|---|---|---|
| `owner` | OneToOneField(User) | Propriétaire de la boutique |
| `name` / `slug` | CharField | Nom et identifiant URL |
| `description` | TextField | Description libre |
| `logo` / `banner` | ImageField | Visuels de la boutique |
| `city` / `country` | CharField | Localisation |
| `is_active` | BooleanField | Boutique visible ou non |

#### `products.Product`
| Champ | Type | Description |
|---|---|---|
| `store` | ForeignKey(Store) | Boutique vendeur |
| `category` | ForeignKey(Category) | Catégorie du produit |
| `name` / `slug` | CharField | Nom et identifiant URL |
| `price` | PositiveIntegerField | Prix en **FCFA (XOF)** |
| `original_price` | PositiveIntegerField | Prix barré (si promo) |
| `badge` | CharField | `new` ou `sale` |
| `is_active` | BooleanField | Produit visible ou non |

#### `products.ProductVariant`
| Champ | Type | Description |
|---|---|---|
| `size` | CharField | Taille (ex. `M`, `XL`) |
| `color` | CharField | Couleur |
| `stock` | PositiveIntegerField | Quantité disponible |

#### `orders.Order`
| Champ | Type | Description |
|---|---|---|
| `user` | ForeignKey(User) | Client |
| `address` | ForeignKey(Address) | Adresse de livraison |
| `status` | CharField | `pending` → `confirmed` → `shipped` → `delivered` / `cancelled` |
| `promo_code` | CharField | Code promo appliqué |
| `discount_amount` | PositiveIntegerField | Montant de la réduction (FCFA) |

---

## Authentification

L'API utilise **JWT (JSON Web Tokens)** via `djangorestframework-simplejwt`.

### Obtenir un token

```http
POST /api/auth/token/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "motdepasse"
}
```

**Réponse :**
```json
{
  "access": "<access_token>",
  "refresh": "<refresh_token>"
}
```

### Utiliser le token

Ajouter l'en-tête à chaque requête protégée :

```http
Authorization: Bearer <access_token>
```

### Rafraîchir le token

```http
POST /api/auth/token/refresh/
Content-Type: application/json

{
  "refresh": "<refresh_token>"
}
```

| Token | Durée de validité |
|---|---|
| `access` | 60 minutes |
| `refresh` | 7 jours |

---

## Référence des endpoints

> **Légende :**
> - 🌐 Public — aucun token requis
> - 🔒 Authentifié — token JWT requis
> - 👤 Propriétaire — token JWT du propriétaire de la ressource

---

### Auth

| Méthode | URL | Accès | Description |
|---|---|---|---|
| `POST` | `/api/auth/token/` | 🌐 | Connexion → obtenir access + refresh token |
| `POST` | `/api/auth/token/refresh/` | 🌐 | Rafraîchir le token d'accès |

---

### Users

| Méthode | URL | Accès | Description |
|---|---|---|---|
| `POST` | `/api/users/register/` | 🌐 | Créer un compte |
| `GET` | `/api/users/me/` | 🔒 | Voir mon profil |
| `PATCH` | `/api/users/me/` | 🔒 | Modifier mon profil (partiel) |
| `PUT` | `/api/users/me/` | 🔒 | Modifier mon profil (complet) |
| `GET` | `/api/users/addresses/` | 🔒 | Lister mes adresses |
| `POST` | `/api/users/addresses/` | 🔒 | Ajouter une adresse |
| `GET` | `/api/users/addresses/{id}/` | 🔒 | Voir une adresse |
| `PATCH` | `/api/users/addresses/{id}/` | 🔒 | Modifier une adresse (partiel) |
| `PUT` | `/api/users/addresses/{id}/` | 🔒 | Modifier une adresse (complet) |
| `DELETE` | `/api/users/addresses/{id}/` | 🔒 | Supprimer une adresse |

**Inscription — corps de requête :**
```json
{
  "email": "fatou@example.com",
  "username": "fatou22",
  "first_name": "Fatou",
  "last_name": "Diallo",
  "password": "monMotDePasse123",
  "password2": "monMotDePasse123"
}
```

**Règle adresse par défaut :** passer `"is_default": true` désactive automatiquement toutes les autres adresses de l'utilisateur.

---

### Stores

| Méthode | URL | Accès | Description |
|---|---|---|---|
| `GET` | `/api/stores/` | 🌐 | Lister les boutiques actives |
| `POST` | `/api/stores/` | 🔒 | Créer ma boutique |
| `GET` | `/api/stores/{slug}/` | 🌐 | Détail d'une boutique |
| `PATCH` | `/api/stores/{slug}/` | 👤 | Modifier ma boutique (partiel) |
| `PUT` | `/api/stores/{slug}/` | 👤 | Modifier ma boutique (complet) |
| `DELETE` | `/api/stores/{slug}/` | 👤 | Supprimer ma boutique |

**Règle :** un utilisateur ne peut posséder qu'**une seule boutique**. Le `slug` est généré automatiquement à partir du nom.

---

### Products

| Méthode | URL | Accès | Description |
|---|---|---|---|
| `GET` | `/api/products/` | 🌐 | Lister les produits (paginé) |
| `GET` | `/api/products/{slug}/` | 🌐 | Fiche produit complète |
| `POST` | `/api/products/{slug}/reviews/` | 🔒 | Poster un avis |
| `GET` | `/api/products/categories/` | 🌐 | Lister les catégories |
| `GET` | `/api/products/categories/{slug}/` | 🌐 | Détail d'une catégorie |

**Filtres disponibles sur `GET /api/products/` :**

| Paramètre | Type | Exemple | Description |
|---|---|---|---|
| `category` | string | `?category=figurines` | Filtrer par slug de catégorie |
| `badge` | string | `?badge=sale` | `new` ou `sale` |
| `store` | string | `?store=dino-shop` | Filtrer par slug de boutique |
| `search` | string | `?search=t-rex` | Recherche dans nom, boutique, catégorie |
| `ordering` | string | `?ordering=-price` | `price`, `-price`, `created_at`, `-created_at` |
| `page` | int | `?page=2` | Page de résultats (20 par page) |

**Règle avis :** un utilisateur ne peut laisser **qu'un seul avis** par produit.

---

### Orders

| Méthode | URL | Accès | Description |
|---|---|---|---|
| `GET` | `/api/orders/` | 🔒 | Historique de mes commandes |
| `POST` | `/api/orders/` | 🔒 | Passer une commande |
| `GET` | `/api/orders/{id}/` | 🔒 | Détail d'une commande |
| `POST` | `/api/orders/{id}/cancel/` | 🔒 | Annuler une commande |

**Passer une commande — corps de requête :**
```json
{
  "address_id": 3,
  "items": [
    { "variant_id": 12, "qty": 2 },
    { "variant_id": 7,  "qty": 1 }
  ]
}
```

**Cycle de vie d'une commande :**

```
pending → confirmed → shipped → delivered
                ↘ cancelled (depuis pending ou confirmed uniquement)
```

**Règle :** les prix unitaires sont figés au moment de la commande — une modification du produit ultérieure n'affecte pas les commandes existantes.

---

### Wishlist

| Méthode | URL | Accès | Description |
|---|---|---|---|
| `GET` | `/api/wishlist/` | 🔒 | Voir ma liste de souhaits |
| `POST` | `/api/wishlist/` | 🔒 | Ajouter un produit |
| `GET` | `/api/wishlist/{id}/` | 🔒 | Voir un item |
| `DELETE` | `/api/wishlist/{id}/` | 🔒 | Retirer un produit |

**Ajouter un produit — corps de requête :**
```json
{ "product_id": 42 }
```

**Idempotent :** ajouter un produit déjà présent retourne l'item existant sans créer de doublon.

---

## Pagination et filtres

Toutes les listes sont paginées avec **20 éléments par page** par défaut.

**Format de réponse paginée :**
```json
{
  "count": 85,
  "next": "http://localhost:8000/api/products/?page=2",
  "previous": null,
  "results": [ ... ]
}
```

Paramètres de pagination :
- `?page=2` — accéder à la page suivante
- La taille de page est fixe (20). Elle peut être modifiée dans `settings/base.py` → `PAGE_SIZE`.

---

## Gestion des fichiers media

Les fichiers uploadés (avatars, images produits, logos boutique) sont stockés dans `media/` et servis sous `/media/`.

| Type de fichier | Dossier de stockage |
|---|---|
| Avatars utilisateurs | `media/avatars/` |
| Images produits | `media/products/` |
| Logos boutiques | `media/stores/logos/` |
| Bannières boutiques | `media/stores/banners/` |

**En développement**, les fichiers sont servis directement par Django (via `static()` dans `urls.py`).

**En production**, configurer le serveur web (Apache/Nginx sur o2switch) pour servir le dossier `media/` statiquement.

---

## Documentation Swagger

La documentation interactive est générée automatiquement par **drf-spectacular** à partir des annotations `@extend_schema` présentes dans les vues.

| URL | Interface | Description |
|---|---|---|
| `/api/docs/` | Swagger UI | Interface interactive — tester les endpoints depuis le navigateur |
| `/api/redoc/` | ReDoc | Documentation lisible — idéale pour la lecture |
| `/api/schema/` | YAML brut | Schéma OpenAPI 3.0 téléchargeable |

### Utiliser Swagger UI

1. Ouvrir `http://localhost:8000/api/docs/`
2. Cliquer sur **Authorize** (icône cadenas)
3. Entrer `Bearer <votre_access_token>`
4. Tester les endpoints directement depuis l'interface

### Générer le schéma YAML manuellement

```bash
python manage.py spectacular --file schema.yml
```

---

## Déploiement en production

### Checklist avant déploiement

- [ ] `DEBUG = False` (automatique avec `production.py`)
- [ ] `SECRET_KEY` longue et aléatoire dans `.env`
- [ ] `ALLOWED_HOSTS` configuré avec le domaine réel
- [ ] `CORS_ALLOWED_ORIGINS` limité au(x) domaine(s) frontend
- [ ] Base MySQL créée et credentials dans `.env`
- [ ] `python manage.py migrate` exécuté
- [ ] `python manage.py collectstatic` exécuté
- [ ] Dossier `media/` accessible en écriture par le serveur web

### Commandes de déploiement

```bash
export DJANGO_SETTINGS_MODULE=config.settings.production

pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```

### Headers de sécurité (activés automatiquement en prod)

| Header | Valeur |
|---|---|
| `X-Frame-Options` | `DENY` |
| `X-Content-Type-Options` | `nosniff` |
| `Strict-Transport-Security` | 1 an + sous-domaines |

---

## Conventions

### Devises
Les prix sont stockés et retournés en **FCFA (XOF)**, entiers. Le XOF n'ayant pas de sous-unité, aucune conversion n'est nécessaire.
Exemple : `5000` = 5 000 FCFA.

### Slugs vs IDs
- Les ressources **publiques** (produits, boutiques, catégories) s'identifient par leur **slug** dans l'URL.
- Les ressources **privées** (adresses, commandes, items wishlist) s'identifient par leur **ID entier**.

### Fuseaux horaires
Le projet utilise le fuseau `Africa/Lagos` (UTC+1). Toutes les dates retournées par l'API sont en ISO 8601 avec fuseau horaire.

### Langue
Les messages d'erreur et validations sont en **français**. La locale Django est `fr-fr`.
