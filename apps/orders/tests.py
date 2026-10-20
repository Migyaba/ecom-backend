from rest_framework.test import APITestCase

from apps.products.models import Category, Product, ProductVariant
from apps.stores.models import Store
from apps.users.models import Address, User
from .models import Order


def make_user(email):
    return User.objects.create_user(email=email, username=email.split('@')[0], password='motDePasse123!')


def make_address(user):
    return Address.objects.create(user=user, full_name='Fatou Diallo', line1='12 rue des Palmiers', city='Abidjan', state='Abidjan')


class OrderTests(APITestCase):
    def setUp(self):
        self.user = make_user('fatou@example.com')
        self.address = make_address(self.user)
        seller = make_user('sade@example.com')
        store = Store.objects.create(owner=seller, name='Sadé Atelier', slug='sade-atelier')
        category = Category.objects.create(name='Femme', slug='femme-test')
        self.product = Product.objects.create(store=store, category=category, name='Robe Ankara', slug='robe-ankara', price=20000)
        self.variant = ProductVariant.objects.create(product=self.product, size='M', stock=3)
        self.client.force_authenticate(self.user)

    def order(self, **overrides):
        payload = {
            'address_id': self.address.pk,
            'items': [{'variant_id': self.variant.pk, 'qty': 2}],
            'delivery_method': 'express',
        }
        payload.update(overrides)
        return self.client.post('/api/orders/', payload, format='json')

    def test_create_order_decrements_stock_and_computes_total(self):
        res = self.order(promo_code='dino10')
        self.assertEqual(res.status_code, 201, res.data)
        self.assertEqual(res.data['subtotal'], 40000)
        self.assertEqual(res.data['discount_amount'], 4000)
        self.assertEqual(res.data['shipping_cost'], 3500)
        self.assertEqual(res.data['total'], 39500)
        self.assertEqual(res.data['promo_code'], 'DINO10')
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.stock, 1)

    def test_free_standard_shipping_above_threshold(self):
        self.variant.stock = 10
        self.variant.save()
        res = self.order(items=[{'variant_id': self.variant.pk, 'qty': 3}], delivery_method='standard')
        self.assertEqual(res.status_code, 201, res.data)
        self.assertEqual(res.data['shipping_cost'], 0)

    def test_rejects_address_of_another_user(self):
        other_address = make_address(make_user('autre@example.com'))
        res = self.order(address_id=other_address.pk)
        self.assertEqual(res.status_code, 400)
        self.assertIn('address_id', res.data)

    def test_rejects_unknown_variant_without_partial_order(self):
        res = self.order(items=[{'variant_id': self.variant.pk, 'qty': 1}, {'variant_id': 9999, 'qty': 1}])
        self.assertEqual(res.status_code, 400)
        self.assertFalse(Order.objects.exists())
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.stock, 3)

    def test_rejects_insufficient_stock(self):
        res = self.order(items=[{'variant_id': self.variant.pk, 'qty': 4}])
        self.assertEqual(res.status_code, 400)
        self.assertIn('items', res.data)

    def test_merges_duplicate_lines_before_stock_check(self):
        res = self.order(items=[{'variant_id': self.variant.pk, 'qty': 2}, {'variant_id': self.variant.pk, 'qty': 2}])
        self.assertEqual(res.status_code, 400)

    def test_rejects_invalid_promo_code(self):
        res = self.order(promo_code='GRATUIT')
        self.assertEqual(res.status_code, 400)
        self.assertIn('promo_code', res.data)

    def test_cancel_restores_stock(self):
        order_id = self.order().data['id']
        res = self.client.post(f'/api/orders/{order_id}/cancel/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['status'], 'cancelled')
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.stock, 3)
        self.assertEqual(self.client.post(f'/api/orders/{order_id}/cancel/').status_code, 400)

    def test_cannot_see_other_users_orders(self):
        order_id = self.order().data['id']
        self.client.force_authenticate(make_user('curieux@example.com'))
        self.assertEqual(self.client.get(f'/api/orders/{order_id}/').status_code, 404)


class PromoCheckTests(APITestCase):
    def test_valid_and_invalid_codes(self):
        res = self.client.get('/api/orders/promo/', {'code': ' dino10 '})
        self.assertEqual(res.data, {'code': 'DINO10', 'percent': 10})
        self.assertEqual(self.client.get('/api/orders/promo/', {'code': 'NOPE'}).status_code, 404)
