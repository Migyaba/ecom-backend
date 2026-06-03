# Ecom-backend

API REST générique pour applications e-commerce multi-vendeurs. Conçue avec **Django** et **Django REST Framework** pour être consommée par n'importe quel frontend (React, Vue, mobile, etc.).

> Ce backend alimente actuellement [DinoMarket](../frontend) — une marketplace de mode et décoration africaine — mais peut être adapté à tout projet e-commerce.

---

## Table des matières

1. [Stack technique](#stack-technique)
2. [Architecture](#architecture)
3. [Prérequis](#prérequis)
4. [Installation](#installation)
5. [Variables d'environnement](#variables-denvironnement)
6. [Base de données](#base-de-données)
7. [Authentification JWT](#authentification-jwt)
8. [Référence des endpoints](#référence-des-endpoints)
9. [Pagination et filtres](#pagination-et-filtres)
10. [Gestion des médias](#gestion-des-médias)
11. [Documentation interactive (Swagger)](#documentation-interactive)
12. [Déploiement](#déploiement)
13. [Conventions](#conventions)

---

## Stack technique

| Composant | Technologie | Version |
|---|---|---|
| Framework web | Django | 6.0.5 |
| API REST | Django REST Framework | 3.17.1 |
| Authentification | djangorestframework-simplejwt | 5.5.1 |
| Documentation | drf-spectacular (OpenAPI 3) | 0.28.0 |
| CORS | django-cors-headers | 4.9.0 |
| Images | Pillow | 12.2.0 |
| BDD développement | SQLite | — |
| BDD production | MySQL 8+ | — |

---

## Architecture

```
backend/
├── config/
│   ├── settings/
│   │   ├── base.py           # Paramètres communs
│   │   ├── development.py    # SQLite · DEBUG=True · emails console
│   │   └── production.py     # MySQL · HTTPS · SMTP
│   ├── urls.py               # Routeur principal + Swagger
│   ├── wsgi.py
│   └── asgi.py
├── apps/
│   ├── users/                # Comptes utilisateurs, profils, adresses
│   ├── stores/               # Boutiques des vendeurs
│   ├── products/             # Catalogue, catégories, avis, témoignages
│   ├── orders/               # Commandes et cycle de vie
│   └── wishlist/             # Listes de souhaits
├── media/                    # Fichiers uploadés (non versionné)
├── manage.py
├── requirements.txt
└── .env                      # Variables d'environnement (non versionné)
```

Chaque application suit la structure standard Django :
`models.py` → `serializers.py` → `views.py` → `urls.py`

---

## Prérequis

- Python **3.12+**
- pip
- *(Production)* MySQL 8+ et un serveur SMTP

---

## Installation

### 1. Cloner le dépôt

```bash
git clone <url-du-repo>
cd backend
```

### 2. Environnement virtuel

```bash
python -m venv .venv
source .venv/bin/activate        # Linux / macOS
# .venv\Scripts\activate         # Windows
```

### 3. Dépendances

```bash
pip install -r requirements.txt
```

### 4. Variables d'environnement

```bash
cp .env.example .env
# Éditer .env avec vos valeurs
```

### 5. Migrations

```bash
python manage.py migrate
```

### 6. Super-utilisateur (optionnel)

```bash
python manage.py createsuperuser
```

### 7. Démarrer

```bash
python manage.py runserver
```

Serveur disponible sur `http://127.0.0.1:8000`.

> Le module `config.settings.development` est chargé par défaut (SQLite, DEBUG=True).  
> Pour la production : `DJANGO_SETTINGS_MODULE=config.settings.production python manage.py runserver`

---

## Variables d'environnement

| Variable | Environnement | Description |
|---|---|---|
| `SECRET_KEY` | Dev + Prod | Clé secrète Django (chaîne aléatoire longue en prod) |
| `ALLOWED_HOSTS` | Prod | Domaines autorisés, séparés par des virgules |
| `CORS_ALLOWED_ORIGINS` | Prod | Origines frontend autorisées (ex. `https://monsite.com`) |
| `DB_NAME` | Prod | Nom de la base MySQL |
| `DB_USER` | Prod | Utilisateur MySQL |
| `DB_PASSWORD` | Prod | Mot de passe MySQL |
| `DB_HOST` | Prod | Hôte MySQL (défaut : `localhost`) |
| `DB_PORT` | Prod | Port MySQL (défaut : `3306`) |
| `EMAIL_HOST` | Prod | Serveur SMTP |
| `EMAIL_PORT` | Prod | Port SMTP (ex. `587`) |
| `EMAIL_HOST_USER` | Prod | Adresse email SMTP |
| `EMAIL_HOST_PASSWORD` | Prod | Mot de passe SMTP |

---

## Base de données

### Développement — SQLite

Aucune configuration requise. Le fichier `db.sqlite3` est créé automatiquement.

### Production — MySQL

Configurée via les variables d'environnement. Encodage `utf8mb4` forcé.

### Commandes utiles

```bash
# Appliquer les migrations
python manage.py migrate

# Créer les migrations après modification d'un modèle
python manage.py makemigrations

# État des migrations
python manage.py showmigrations
```

### Modèles principaux

#### `users.User`
| Champ | Type | Notes |
|---|---|---|
| `email` | EmailField unique | Identifiant de connexion |
| `username` | CharField | Nom d'utilisateur |
| `first_name` / `last_name` | CharField | Nom complet |
| `phone` | CharField | Téléphone |
| `avatar` | ImageField | Photo de profil |

#### `stores.Store`
| Champ | Type | Notes |
|---|---|---|
| `owner` | OneToOneField(User) | Un vendeur = une boutique |
| `name` / `slug` | CharField | Slug auto-généré |
| `logo` / `banner` | ImageField | Visuels |
| `is_active` | BooleanField | Visibilité publique |

#### `products.Product`
| Champ | Type | Notes |
|---|---|---|
| `store` | ForeignKey(Store) | Boutique propriétaire |
| `category` | ForeignKey(Category) | Catégorie |
| `price` | PositiveIntegerField | Prix entier (FCFA) |
| `original_price` | PositiveIntegerField | Prix barré (promo) |
| `badge` | CharField | `new` ou `sale` |

#### `orders.Order`
| Champ | Type | Notes |
|---|---|---|
| `user` | ForeignKey(User) | Client |
| `address` | ForeignKey(Address) | Adresse de livraison |
| `status` | CharField | `pending` → `confirmed` → `shipped` → `delivered` / `cancelled` |
| `discount_amount` | PositiveIntegerField | Réduction appliquée |

---

## Authentification JWT

L'API utilise **JSON Web Tokens** via `djangorestframework-simplejwt`.

### Connexion

```http
POST /api/auth/token/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "motdepasse"
}
```

```json
{
  "access": "<access_token>",
  "refresh": "<refresh_token>"
}
```

### Utilisation

```http
Authorization: Bearer <access_token>
```

### Rafraîchissement

```http
POST /api/auth/token/refresh/
Content-Type: application/json

{ "refresh": "<refresh_token>" }
```

| Token | Durée |
|---|---|
| `access` | 60 minutes |
| `refresh` | 7 jours |

---

## Référence des endpoints

> 🌐 Public — 🔒 JWT requis — 👤 Propriétaire de la ressource

### Auth

| Méthode | URL | Accès | Description |
|---|---|---|---|
| `POST` | `/api/auth/token/` | 🌐 | Connexion → tokens JWT |
| `POST` | `/api/auth/token/refresh/` | 🌐 | Rafraîchir l'access token |

### Users

| Méthode | URL | Accès | Description |
|---|---|---|---|
| `POST` | `/api/users/register/` | 🌐 | Créer un compte |
| `GET` | `/api/users/me/` | 🔒 | Mon profil |
| `PATCH` | `/api/users/me/` | 🔒 | Modifier mon profil |
| `GET` | `/api/users/addresses/` | 🔒 | Mes adresses |
| `POST` | `/api/users/addresses/` | 🔒 | Ajouter une adresse |
| `PATCH` | `/api/users/addresses/{id}/` | 🔒 | Modifier une adresse |
| `DELETE` | `/api/users/addresses/{id}/` | 🔒 | Supprimer une adresse |

**Corps d'inscription :**
```json
{
  "email": "fatou@example.com",
  "username": "fatou22",
  "first_name": "Fatou",
  "last_name": "Diallo",
  "password": "motDePasse123",
  "password2": "motDePasse123"
}
```

### Stores

| Méthode | URL | Accès | Description |
|---|---|---|---|
| `GET` | `/api/stores/` | 🌐 | Lister les boutiques actives |
| `POST` | `/api/stores/` | 🔒 | Créer ma boutique |
| `GET` | `/api/stores/{slug}/` | 🌐 | Détail d'une boutique |
| `PATCH` | `/api/stores/{slug}/` | 👤 | Modifier ma boutique |
| `DELETE` | `/api/stores/{slug}/` | 👤 | Supprimer ma boutique |

> Un utilisateur ne peut posséder qu'**une seule boutique**.

### Products

| Méthode | URL | Accès | Description |
|---|---|---|---|
| `GET` | `/api/products/` | 🌐 | Lister les produits (paginé + filtres) |
| `GET` | `/api/products/{slug}/` | 🌐 | Fiche produit complète |
| `POST` | `/api/products/{slug}/reviews/` | 🔒 | Poster un avis |
| `GET` | `/api/products/categories/` | 🌐 | Lister les catégories |
| `GET` | `/api/products/categories/{slug}/` | 🌐 | Détail d'une catégorie |
| `GET` | `/api/products/testimonials/` | 🌐 | Témoignages homepage |

**Filtres disponibles sur `GET /api/products/` :**

| Paramètre | Exemple | Description |
|---|---|---|
| `category` | `?category=women` | Slug de catégorie |
| `badge` | `?badge=sale` | `new` ou `sale` |
| `store` | `?store=sade-atelier` | Slug de boutique |
| `search` | `?search=robe` | Recherche textuelle |
| `ordering` | `?ordering=-price` | `price`, `-price`, `created_at`, `-created_at` |
| `page` | `?page=2` | Page (20 résultats/page) |

### Orders

| Méthode | URL | Accès | Description |
|---|---|---|---|
| `GET` | `/api/orders/` | 🔒 | Historique de mes commandes |
| `POST` | `/api/orders/` | 🔒 | Passer une commande |
| `GET` | `/api/orders/{id}/` | 🔒 | Détail d'une commande |
| `POST` | `/api/orders/{id}/cancel/` | 🔒 | Annuler une commande |

**Corps de commande :**
```json
{
  "address_id": 3,
  "items": [
    { "variant_id": 12, "qty": 2 },
    { "variant_id": 7,  "qty": 1 }
  ]
}
```

**Cycle de vie :**
```
pending → confirmed → shipped → delivered
               ↘ cancelled (depuis pending ou confirmed)
```

### Wishlist

| Méthode | URL | Accès | Description |
|---|---|---|---|
| `GET` | `/api/wishlist/` | 🔒 | Ma liste de souhaits |
| `POST` | `/api/wishlist/` | 🔒 | Ajouter un produit |
| `DELETE` | `/api/wishlist/{id}/` | 🔒 | Retirer un produit |

```json
{ "product_id": 42 }
```

---

## Pagination et filtres

Toutes les listes sont paginées — **20 éléments par page** par défaut.

```json
{
  "count": 85,
  "next": "http://localhost:8000/api/products/?page=2",
  "previous": null,
  "results": []
}
```

---

## Gestion des médias

| Type | Chemin de stockage |
|---|---|
| Avatars | `media/avatars/` |
| Images produits | `media/products/` |
| Logos boutiques | `media/stores/logos/` |
| Bannières | `media/stores/banners/` |

Les médias sont servis sous `/media/` (par Django en dev, par le serveur web en prod).

---

## Documentation interactive

Générée automatiquement par **drf-spectacular** depuis les annotations `@extend_schema`.

| URL | Interface |
|---|---|
| `/api/docs/` | Swagger UI — tester les endpoints depuis le navigateur |
| `/api/redoc/` | ReDoc — documentation lisible |
| `/api/schema/` | Schéma OpenAPI 3.0 brut (YAML) |

### Authentifier dans Swagger UI

1. Ouvrir `http://localhost:8000/api/docs/`
2. Cliquer **Authorize** (icône cadenas)
3. Saisir `Bearer <votre_access_token>`

### Exporter le schéma

```bash
python manage.py spectacular --file schema.yml
```

---

## Déploiement

### Checklist

- [ ] `SECRET_KEY` longue et unique dans `.env`
- [ ] `DEBUG = False` (automatique avec `production.py`)
- [ ] `ALLOWED_HOSTS` configuré avec le domaine réel
- [ ] `CORS_ALLOWED_ORIGINS` limité aux origines frontend
- [ ] Base MySQL créée, credentials dans `.env`
- [ ] `python manage.py migrate` exécuté
- [ ] `python manage.py collectstatic` exécuté
- [ ] Dossier `media/` accessible en écriture par le serveur

### Commandes

```bash
export DJANGO_SETTINGS_MODULE=config.settings.production

pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```

### En-têtes de sécurité (prod)

| Header | Valeur |
|---|---|
| `X-Frame-Options` | `DENY` |
| `X-Content-Type-Options` | `nosniff` |
| `Strict-Transport-Security` | 1 an + sous-domaines |

---

## Conventions

### Devises
Les prix sont des entiers en **FCFA (XOF)**. `5000` = 5 000 FCFA. Aucune conversion ni décimale.

### Slugs vs IDs
- Ressources **publiques** (produits, boutiques, catégories) → **slug** dans l'URL
- Ressources **privées** (adresses, commandes, wishlist) → **ID entier**

### Fuseaux horaires
Fuseau `Africa/Lagos` (UTC+1). Toutes les dates ISO 8601 avec fuseau.

### Langue
Messages d'erreur et validations en **français**. Locale Django : `fr-fr`.

### Intégration avec un nouveau frontend
Ce backend expose uniquement une API JSON — aucun couplage avec un frontend spécifique.  
Pour connecter un nouveau frontend :
1. Configurer `CORS_ALLOWED_ORIGINS` dans `.env` avec l'origine de votre frontend
2. Pointer vos appels API vers `http://<host>/api/`
3. Implémenter le flux JWT : `POST /api/auth/token/` → stocker → `Authorization: Bearer`
4. Consulter `/api/docs/` pour la documentation complète
