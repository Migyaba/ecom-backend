"""Helpers d'affichage partagés par les écrans de l'admin."""
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

# Couleur du badge (variantes Unfold) pour chaque statut de commande
ORDER_STATUS_VARIANTS = {
    'pending': 'warning',
    'confirmed': 'info',
    'shipped': 'primary',
    'delivered': 'success',
    'cancelled': 'danger',
}

ORDER_STATUS_LABELS = {
    'pending': 'En attente',
    'confirmed': 'Confirmée',
    'shipped': 'Expédiée',
    'delivered': 'Livrée',
    'cancelled': 'Annulée',
}


def format_fcfa(amount):
    # Espaces insécables : « 42 500 FCFA » ne se coupe jamais en fin de ligne
    return f"{amount or 0:,}".replace(',', '\u202f') + '\u00a0FCFA'


def header_with_image(title, subtitle, image_url):
    """Colonne « en-tête » Unfold : titre, sous-titre et miniature carrée (ou initiales à défaut)."""
    if image_url:
        return [title, subtitle, None, {'path': image_url, 'squared': True, 'width': 44, 'height': 44}]
    return [title, subtitle, (title or '?')[:2]]


def badge(text, variant=None):
    return mark_safe(render_to_string('unfold/helpers/label.html', {'text': text, 'variant': variant}))


def order_status_badge(status):
    return badge(ORDER_STATUS_LABELS.get(status, status), ORDER_STATUS_VARIANTS.get(status))
