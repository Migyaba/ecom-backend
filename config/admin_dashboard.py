"""Callbacks Unfold : tableau de bord d'accueil, badge de la sidebar, bandeau d'environnement."""
import json
from datetime import timedelta

from django.conf import settings
from django.db.models import F, Q, Sum
from django.db.models.functions import Coalesce, TruncDate
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html

from apps.orders.models import Order, OrderItem
from apps.products.models import Product
from config.admin_utils import badge, format_fcfa, order_status_badge

CHART_DAYS = 14


def _revenue(orders):
    """CA d'un ensemble de commandes : lignes − réductions + livraison."""
    lines = OrderItem.objects.filter(order__in=orders).aggregate(
        total=Coalesce(Sum(F('unit_price') * F('qty')), 0)
    )['total']
    extras = orders.aggregate(
        shipping=Coalesce(Sum('shipping_cost'), 0),
        discount=Coalesce(Sum('discount_amount'), 0),
    )
    return lines - extras['discount'] + extras['shipping']


def _low_stock_products():
    return (
        Product.objects.filter(is_active=True)
        .annotate(total_stock=Coalesce(Sum('variants__stock'), 0))
        .filter(total_stock__lte=settings.LOW_STOCK_THRESHOLD)
        .select_related('store')
        .order_by('total_stock', 'name')
    )


def _sales_chart(valid_orders, today):
    start = today - timedelta(days=CHART_DAYS - 1)
    per_day = dict(
        OrderItem.objects.filter(order__in=valid_orders, order__created_at__date__gte=start)
        .annotate(day=TruncDate('order__created_at'))
        .values_list('day')
        .annotate(total=Sum(F('unit_price') * F('qty')))
    )
    days = [start + timedelta(days=i) for i in range(CHART_DAYS)]
    return json.dumps({
        'labels': [d.strftime('%d/%m') for d in days],
        'datasets': [{
            'label': 'Ventes (FCFA)',
            'data': [per_day.get(d, 0) for d in days],
            'backgroundColor': 'var(--color-primary-600)',
            'borderRadius': 4,
            'maxBarThickness': 36,
        }],
    })


def dashboard_callback(request, context):
    today = timezone.localdate()
    valid = Order.objects.exclude(status='cancelled')
    orders_url = reverse('admin:orders_order_changelist')
    products_url = reverse('admin:products_product_changelist')
    low_stock = _low_stock_products()
    pending_count = Order.objects.filter(status='pending').count()

    recent = Order.objects.select_related('user').prefetch_related('items').order_by('-created_at')[:8]
    recent_rows = [
        [
            format_html('<a href="{}" class="text-primary-600 font-semibold">#{}</a>', reverse('admin:orders_order_change', args=[o.pk]), o.pk),
            (o.user.get_full_name() or o.user.email) if o.user else '—',
            order_status_badge(o.status),
            format_fcfa(o.total),
            timezone.localtime(o.created_at).strftime('%d/%m %H:%M'),
        ]
        for o in recent
    ]
    low_rows = [
        [
            format_html('<a href="{}" class="text-primary-600 font-semibold">{}</a>', reverse('admin:products_product_change', args=[p.pk]), p.name),
            p.store.name,
            badge(f'{p.total_stock} en stock', 'danger' if p.total_stock == 0 else 'warning'),
        ]
        for p in low_stock[:8]
    ]

    context.update({
        'kpis': [
            {'title': "Ventes aujourd'hui", 'value': format_fcfa(_revenue(valid.filter(created_at__date=today))),
             'footer': f"{valid.filter(created_at__date=today).count()} commande(s)", 'href': orders_url},
            {'title': 'Ventes du mois', 'value': format_fcfa(_revenue(valid.filter(created_at__year=today.year, created_at__month=today.month))),
             'footer': f"{valid.filter(created_at__year=today.year, created_at__month=today.month).count()} commande(s)", 'href': orders_url},
            {'title': 'Commandes à traiter', 'value': pending_count,
             'footer': 'En attente de confirmation', 'href': f'{orders_url}?status__exact=pending'},
            {'title': 'Stock bas', 'value': low_stock.count(),
             'footer': f'Produits à {settings.LOW_STOCK_THRESHOLD} unités ou moins', 'href': products_url},
        ],
        'sales_chart': _sales_chart(valid, today),
        'recent_orders': {'headers': ['N°', 'Client', 'Statut', 'Total', 'Date'], 'rows': recent_rows},
        'low_stock': {'headers': ['Produit', 'Boutique', 'Stock'], 'rows': low_rows},
        'orders_url': orders_url,
    })
    return context


def pending_orders_badge(request):
    count = Order.objects.filter(status='pending').count()
    return count or None


def environment_callback(request):
    return ['Développement', 'info'] if settings.DEBUG else ['Production', 'danger']
