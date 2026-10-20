from rest_framework.test import APITestCase

from apps.stores.models import Store
from apps.users.models import User
from .models import Category, Product, ProductImage, ProductVariant


class ProductTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='fatou@example.com', username='fatou', password='motDePasse123!')
        store = Store.objects.create(owner=self.user, name='Sadé Atelier', slug='sade-atelier')
        category = Category.objects.create(name='Femme', slug='femme-test')
        self.product = Product.objects.create(store=store, category=category, name='Robe Ankara', slug='robe-ankara', price=20000)
        ProductImage.objects.create(product=self.product, image_url='https://example.com/a.jpg', order=0)
        ProductImage.objects.create(product=self.product, image_url='https://example.com/b.jpg', order=1, is_cover=True)
        ProductVariant.objects.create(product=self.product, size='S', stock=0)
        self.in_stock = ProductVariant.objects.create(product=self.product, size='M', stock=2)

    def test_list_exposes_cover_and_default_variant(self):
        res = self.client.get('/api/products/')
        item = res.data['results'][0]
        self.assertEqual(item['cover'], 'https://example.com/b.jpg')
        self.assertEqual(item['default_variant']['id'], self.in_stock.pk)
        self.assertEqual(item['default_variant']['size'], 'M')

    def test_review_rating_must_be_between_1_and_5(self):
        self.client.force_authenticate(self.user)
        res = self.client.post('/api/products/robe-ankara/reviews/', {'rating': 6, 'body': 'Top'}, format='json')
        self.assertEqual(res.status_code, 400)

    def test_second_review_is_rejected_with_400(self):
        self.client.force_authenticate(self.user)
        url = '/api/products/robe-ankara/reviews/'
        self.assertEqual(self.client.post(url, {'rating': 5, 'body': 'Top'}, format='json').status_code, 201)
        self.assertEqual(self.client.post(url, {'rating': 4, 'body': 'Encore'}, format='json').status_code, 400)
