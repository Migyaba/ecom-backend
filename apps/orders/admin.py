from django.contrib import admin, messages
from django.db.models import Count
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.html import format_html
from unfold.admin import ModelAdmin, TabularInline
from unfold.contrib.filters.admin import ChoicesDropdownFilter, RangeDateFilter
from unfold.decorators import action, display

from config.admin_utils import ORDER_STATUS_LABELS, ORDER_STATUS_VARIANTS, format_fcfa, order_status_badge
from .models import Order, OrderItem


class OrderItemInline(TabularInline):
    model = OrderItem
    extra = 0
    fields = ('product_name', 'variant', 'unit_price', 'qty', 'line_total_display')
    readonly_fields = fields
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

    @display(description='Total ligne')
    def line_total_display(self, obj):
        return format_fcfa(obj.line_total)


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = ('number', 'customer', 'status_badge', 'items_count', 'total_display', 'delivery_method', 'payment_method', 'created_at')
    list_display_links = ('number',)
    list_filter = (
        ('status', ChoicesDropdownFilter),
        ('delivery_method', ChoicesDropdownFilter),
        ('payment_method', ChoicesDropdownFilter),
        ('created_at', RangeDateFilter),
    )
    list_filter_submit = True
    search_fields = ('id', 'user__email', 'user__first_name', 'user__last_name', 'promo_code')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    list_per_page = 30
    inlines = (OrderItemInline,)
    readonly_fields = (
        'status_detail', 'customer_link', 'shipping_address',
        'subtotal_display', 'discount_display', 'shipping_display', 'total_display',
        'promo_code', 'delivery_method', 'payment_method', 'created_at', 'updated_at',
    )
    fieldsets = (
        ('Commande', {'fields': ('status_detail', 'created_at', 'updated_at')}),
        ('Client', {'fields': ('customer_link', 'shipping_address')}),
        ('Livraison et paiement', {'fields': ('delivery_method', 'payment_method', 'promo_code')}),
        ('Montants', {'fields': ('subtotal_display', 'discount_display', 'shipping_display', 'total_display')}),
    )
    actions = ('bulk_confirm', 'bulk_ship')
    actions_row = ('row_advance', 'row_cancel')
    actions_detail = ('detail_advance', 'detail_cancel')

    def get_queryset(self, request):
        return (
            super().get_queryset(request)
            .select_related('user', 'address')
            .prefetch_related('items')
            .annotate(items_total=Count('items'))
        )

    # Les commandes naissent du checkout : pas de création manuelle, et on annule au lieu de supprimer
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    # ── Colonnes ──────────────────────────────────────────────────
    @display(description='N°', ordering='id')
    def number(self, obj):
        return f'#{obj.pk}'

    @display(description='Client', ordering='user__email', header=True)
    def customer(self, obj):
        if not obj.user:
            return ['Compte supprimé', '']
        return [obj.user.get_full_name() or obj.user.email, obj.user.email]

    @display(description='Statut', ordering='status', label=ORDER_STATUS_VARIANTS)
    def status_badge(self, obj):
        return obj.status, ORDER_STATUS_LABELS.get(obj.status, obj.status)

    @display(description='Statut')
    def status_detail(self, obj):
        return order_status_badge(obj.status)

    @display(description='Articles', ordering='items_total')
    def items_count(self, obj):
        return obj.items_total if hasattr(obj, 'items_total') else obj.items.count()

    @display(description='Total')
    def total_display(self, obj):
        return format_fcfa(obj.total)

    @display(description='Sous-total')
    def subtotal_display(self, obj):
        return format_fcfa(obj.subtotal)

    @display(description='Réduction')
    def discount_display(self, obj):
        return f'− {format_fcfa(obj.discount_amount)}' if obj.discount_amount else '—'

    @display(description='Livraison')
    def shipping_display(self, obj):
        return format_fcfa(obj.shipping_cost) if obj.shipping_cost else 'Gratuite'

    @display(description='Client')
    def customer_link(self, obj):
        if not obj.user:
            return '—'
        url = reverse('admin:users_user_change', args=[obj.user_id])
        phone = f' · {obj.user.phone}' if obj.user.phone else ''
        return format_html('<a href="{}" class="text-primary-600">{}</a>{}', url, obj.user.get_full_name() or obj.user.email, f' ({obj.user.email}){phone}')

    @display(description='Adresse de livraison')
    def shipping_address(self, obj):
        a = obj.address
        if not a:
            return '—'
        lines = [a.full_name, a.line1, a.line2, f'{a.city}, {a.state}', a.country]
        return format_html('<br>'.join(['{}'] * len([line for line in lines if line])), *[line for line in lines if line])

    # ── Changements de statut ─────────────────────────────────────
    def _advance(self, request, order):
        previous = order.get_status_display()
        if order.advance():
            messages.success(request, f'Commande #{order.pk} : {previous} → {ORDER_STATUS_LABELS[order.status]}.')
        else:
            messages.warning(request, f'La commande #{order.pk} ne peut plus avancer ({ORDER_STATUS_LABELS[order.status]}).')

    def _cancel(self, request, order):
        if order.cancel():
            messages.success(request, f'Commande #{order.pk} annulée, stock restitué.')
        else:
            messages.warning(request, f'La commande #{order.pk} ne peut plus être annulée ({ORDER_STATUS_LABELS[order.status]}).')

    @action(description='Étape suivante', icon='arrow_forward', permissions=['change'])
    def row_advance(self, request, object_id):
        self._advance(request, Order.objects.get(pk=object_id))
        return redirect(request.headers.get('referer') or reverse('admin:orders_order_changelist'))

    @action(description='Annuler', icon='cancel', permissions=['change'])
    def row_cancel(self, request, object_id):
        self._cancel(request, Order.objects.get(pk=object_id))
        return redirect(request.headers.get('referer') or reverse('admin:orders_order_changelist'))

    @action(description='Étape suivante', icon='arrow_forward', permissions=['change'])
    def detail_advance(self, request, object_id):
        self._advance(request, Order.objects.get(pk=object_id))
        return redirect(reverse('admin:orders_order_change', args=[object_id]))

    @action(description='Annuler la commande', icon='cancel', permissions=['change'])
    def detail_cancel(self, request, object_id):
        self._cancel(request, Order.objects.get(pk=object_id))
        return redirect(reverse('admin:orders_order_change', args=[object_id]))

    @action(description='Confirmer les commandes sélectionnées', permissions=['change'])
    def bulk_confirm(self, request, queryset):
        done = sum(order.advance() for order in queryset.filter(status='pending'))
        messages.success(request, f'{done} commande(s) confirmée(s).')

    @action(description='Marquer comme expédiées', permissions=['change'])
    def bulk_ship(self, request, queryset):
        done = sum(order.advance() for order in queryset.filter(status='confirmed'))
        messages.success(request, f'{done} commande(s) expédiée(s).')
