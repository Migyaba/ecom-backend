#!/bin/sh
set -e

# Applique les migrations à chaque démarrage (no-op si la base est à jour)
python manage.py migrate --noinput

exec "$@"
