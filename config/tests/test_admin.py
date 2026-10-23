from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from apps.orders.models import Order, OrderItem
from apps.products.models import Category, Product, ProductImage, ProductVariant, Review, Testimonial
from apps.stores.models import Store
from apps.users.models import Address, User
from apps.wishlist.models import WishlistItem


class AdminSmokeTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_superuser(email='admin@example.com', username='admin', password='x')
        store = Store.objects.create(owner=cls.admin, name='Sadé Atelier', slug='sade-atelier')
        category = Category.objects.create(name='Femme', slug='femme-test')
        cls.product = Product.objects.create(store=store, category=category, name='Robe Ankara', slug='robe-ankara', price=20000, original_price=25000, badge='sale')
        ProductImage.objects.create(product=cls.product, image_url='https://example.com/a.jpg', is_cover=True)
        cls.variant = ProductVariant.objects.create(product=cls.product, size='M', stock=1)
        address = Address.objects.create(user=cls.admin, full_name='Fatou Diallo', line1='12 rue', city='Abidjan', state='Abidjan')
        cls.order = Order.objects.create(user=cls.admin, address=address, shipping_cost=2500)
        OrderItem.objects.create(order=cls.order, variant=cls.variant, product_name='Robe Ankara', unit_price=20000, qty=2)
        Review.objects.create(product=cls.product, user=cls.admin, rating=5, body='Superbe')
        Testimonial.objects.create(name='Awa', city='Dakar', text='Top')
        WishlistItem.objects.create(user=cls.admin, product=cls.product)

    def setUp(self):
        self.client.force_login(self.admin)

    def test_admin_lives_under_configured_url(self):
        self.assertEqual(reverse('admin:index'), '/' + settings.ADMIN_URL)

    def test_dashboard(self):
        res = self.client.get(reverse('admin:index'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Commandes à traiter')
        self.assertContains(res, 'Robe Ankara')  # stock bas
        self.assertContains(res, '42\u202f500\u00a0FCFA')  # 2 × 20 000 + 2 500 de livraison

    def test_every_changelist_and_change_page_renders(self):
        objects = {
            'orders_order': self.order, 'products_product': self.product, 'products_category': self.product.category,
            'products_review': Review.objects.first(), 'products_testimonial': Testimonial.objects.first(),
            'stores_store': self.product.store, 'users_user': self.admin, 'users_address': Address.objects.first(),
            'wishlist_wishlistitem': WishlistItem.objects.first(),
        }
        for name, obj in objects.items():
            with self.subTest(name=name):
                self.assertEqual(self.client.get(reverse(f'admin:{name}_changelist')).status_code, 200)
                self.assertEqual(self.client.get(reverse(f'admin:{name}_change', args=[obj.pk])).status_code, 200)
        for name in ('products_product', 'users_user', 'auth_group'):
            with self.subTest(add=name):
                self.assertEqual(self.client.get(reverse(f'admin:{name}_add')).status_code, 200)

    def test_create_user_with_email(self):
        res = self.client.post(reverse('admin:users_user_add'), {
            'email': 'nouveau@example.com', 'username': 'nouveau',
            'usable_password': 'true', 'password1': 'unMotDePasse!2026', 'password2': 'unMotDePasse!2026',
        })
        self.assertEqual(res.status_code, 302, res.context and res.context['errors'])
        self.assertTrue(User.objects.filter(email='nouveau@example.com').exists())

    def test_row_actions_advance_then_cancel_restores_stock(self):
        self.client.get(reverse('admin:orders_order_row_advance', args=[self.order.pk]))
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'confirmed')

        self.client.get(reverse('admin:orders_order_row_cancel', args=[self.order.pk]))
        self.order.refresh_from_db()
        self.variant.refresh_from_db()
        self.assertEqual(self.order.status, 'cancelled')
        self.assertEqual(self.variant.stock, 3)

    def test_product_stock_filter(self):
        res = self.client.get(reverse('admin:products_product_changelist'), {'stock': 'low'})
        self.assertContains(res, 'Robe Ankara')
