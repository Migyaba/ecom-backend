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
| Serveur WSGI | Gunicorn (+ WhiteNoise) | 23.0.0 |
| Stockage médias (prod) | django-storages → MinIO (S3) | 1.14.6 |
| Interface d'administration | django-unfold | 0.110.0 |
| API REST | Django REST Framework | 3.17.1 |
| Authentification | djangorestframework-simplejwt | 5.5.1 |
| Documentation | drf-spectacular (OpenAPI 3) | 0.28.0 |
| CORS | django-cors-headers | 4.9.0 |
| Images | Pillow | 12.2.0 |
| BDD développement | SQLite | — |
| BDD production | PostgreSQL | — |

---

## Architecture

```
backend/
├── config/
│   ├── settings/
│   │   ├── base.py           # Paramètres communs
│   │   ├── development.py    # SQLite · DEBUG=True · emails console
│   │   └── production.py     # PostgreSQL · HTTPS · SMTP
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
- *(Production)* PostgreSQL et un serveur SMTP

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
| `DB_NAME` | Prod | Nom de la base PostgreSQL |
| `DB_USER` | Prod | Utilisateur PostgreSQL |
| `DB_PASSWORD` | Prod | Mot de passe PostgreSQL |
| `DB_HOST` | Prod | Hôte PostgreSQL (défaut : `localhost`) |
| `DB_PORT` | Prod | Port PostgreSQL (défaut : `5432`) |
| `EMAIL_HOST` | Prod | Serveur SMTP |
| `EMAIL_PORT` | Prod | Port SMTP (ex. `587`) |
| `EMAIL_HOST_USER` | Prod | Adresse email SMTP |
| `EMAIL_HOST_PASSWORD` | Prod | Mot de passe SMTP |

---

## Base de données

### Développement — SQLite

Aucune configuration requise. Le fichier `db.sqlite3` est créé automatiquement.

### Production — PostgreSQL

Configurée via les variables d'environnement.

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

> `/api/auth/token/` et `/api/users/register/` sont limités à 10 requêtes/minute par IP.

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
  ],
  "delivery_method": "standard",
  "payment_method": "pod",
  "promo_code": "DINO10"
}
```

- L'adresse doit appartenir à l'utilisateur connecté.
- Le stock des variantes est vérifié puis décrémenté (restitué en cas d'annulation).
- `delivery_method` : `express` (3 500), `standard` (2 500, gratuit au-delà de 50 000), `pickup` (0).
- `payment_method` : `card`, `transfer`, `pod` (paiement à la livraison).
- `promo_code` : validé côté serveur (`PROMO_CODES` dans `settings/base.py`).
- Total = sous-total − réduction + frais de livraison.

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

En développement, les médias sont écrits dans `media/` et servis par Django sous `/media/`.
En production, ils sont stockés dans le bucket MinIO (`MINIO_BUCKET`) et les URLs renvoyées par l'API pointent vers `MINIO_PUBLIC_DOMAIN`.

---

## Administration

L'admin Django utilise le thème **Unfold**, aux couleurs DinoMarket.

| Élément | Où |
|---|---|
| URL | `/<ADMIN_URL>` — à définir dans `.env` (évite le `/admin/` par défaut) |
| Tableau de bord | ventes du jour et du mois, commandes à traiter, stock bas, graphique 14 jours, dernières commandes — `config/admin_dashboard.py` + `templates/admin/index.html` |
| Menu latéral, couleurs, logo | `UNFOLD` dans `config/settings/base.py`, logos dans `static/admin/` |
| Commandes | actions « Étape suivante » / « Annuler » (restitue le stock) par ligne, dans la fiche et en masse ; création et suppression désactivées |
| Produits | miniature, stock total avec alerte (`LOW_STOCK_THRESHOLD`), filtre rupture/stock bas, activation en masse |

Créer un compte administrateur :

```bash
python manage.py createsuperuser                                                        # en local
docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser    # sur le VPS
```

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

Le backend est déployé en **Docker sur un VPS**, derrière un **Traefik** existant, par GitHub Actions ([`.github/workflows/deploy.yml`](.github/workflows/deploy.yml)).

### Pipeline

| Événement | Jobs |
|---|---|
| Pull request vers `master` | `test` (check Django, migrations à jour, tests) |
| Push sur `master` / lancement manuel | `test` → `build` (image poussée sur `ghcr.io/migyaba/ecom-backend`) → `deploy` (SSH sur le VPS) |

Le job `deploy` copie `docker-compose.prod.yml` sur le VPS, récupère l'image du commit (`sha-<commit>`) et relance la stack avec `docker compose up -d --wait`. Les migrations sont appliquées au démarrage du conteneur (`docker/entrypoint.sh`).

### Stack (`docker-compose.prod.yml`)

| Service | Rôle |
|---|---|
| `db` | PostgreSQL 16, données dans le volume `pgdata` |
| `web` | Django + Gunicorn ; fichiers statiques servis par WhiteNoise |

`web` est exposé par Traefik via ses labels ; `db` n'est joignable que sur le réseau interne.
Les fichiers uploadés (images produits, avatars, logos) sont stockés dans **MinIO** (voir ci-dessous).

### Mise en place (une seule fois)

**1. Sur le VPS**

```bash
sudo mkdir -p /opt/ecom-backend && sudo chown $USER /opt/ecom-backend
cd /opt/ecom-backend
nano .env          # partir de .env.example (SECRET_KEY, DB_PASSWORD, domaine, Traefik…)
chmod 600 .env
```

Vérifier dans `.env` que `TRAEFIK_NETWORK`, `TRAEFIK_ENTRYPOINT` et `TRAEFIK_CERTRESOLVER` correspondent à la configuration de Traefik (`docker network ls`, fichier `traefik.yml`).

L'utilisateur SSH doit pouvoir lancer `docker` (membre du groupe `docker`).

**2. Sur GitHub** (*Settings → Secrets and variables → Actions*)

| Type | Nom | Valeur |
|---|---|---|
| Secret | `VPS_HOST` | IP ou nom du VPS |
| Secret | `VPS_USER` | Utilisateur SSH |
| Secret | `VPS_SSH_KEY` | Clé privée SSH (la clé publique dans `~/.ssh/authorized_keys` du VPS) |
| Secret | `VPS_PORT` | *(optionnel)* port SSH, 22 par défaut |
| Variable | `VPS_APP_DIR` | *(optionnel)* dossier sur le VPS, `/opt/ecom-backend` par défaut |

Le job `deploy` utilise l'environnement GitHub `production` : on peut y ajouter une validation manuelle avant chaque déploiement.

**3. MinIO** : créer le bucket, le rendre lisible publiquement et un utilisateur dédié à Django

```bash
mc alias set vps https://minio.miguelmissetcho.com <admin> <motdepasse>
mc mb vps/ecom-media
mc anonymous set download vps/ecom-media          # lecture publique (URLs stables)

cat > ecom-media-rw.json <<'JSON'
{
  "Version": "2012-10-17",
  "Statement": [
    {"Effect": "Allow", "Action": ["s3:ListBucket"], "Resource": ["arn:aws:s3:::ecom-media"]},
    {"Effect": "Allow", "Action": ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"], "Resource": ["arn:aws:s3:::ecom-media/*"]}
  ]
}
JSON
mc admin policy create vps ecom-media-rw ecom-media-rw.json
mc admin user add vps ecom-backend <secret-long>
mc admin policy attach vps ecom-media-rw --user ecom-backend
```

Renseigner ensuite `MINIO_*` dans `.env` :
- `MINIO_ENDPOINT_URL` : URL de l'API S3 vue depuis le conteneur Django — `http://<conteneur-minio>:9000` si MinIO est sur le même réseau Docker (ex. le réseau Traefik), sinon l'URL publique de l'API.
- `MINIO_PUBLIC_DOMAIN` : domaine public + bucket (`minio.miguelmissetcho.com/ecom-media`), utilisé dans les URLs renvoyées au frontend.

Pour reprendre des médias existants : `mc mirror ./media/ vps/ecom-media/`.

**4. DNS** : faire pointer `BACKEND_DOMAIN` vers l'IP du VPS.

### Commandes utiles sur le VPS

```bash
cd /opt/ecom-backend
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs -f web
docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser

# Sauvegarde de la base
docker compose -f docker-compose.prod.yml exec -T db pg_dump -U dinomarket_user dinomarket > backup.sql
```

### Construire et lancer l'image en local

```bash
docker build -t ecom-backend .
```

`GET /healthz/` répond `{"status": "ok"}` ; il sert au healthcheck Docker.

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
