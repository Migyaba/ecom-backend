from rest_framework.test import APITestCase

from apps.users.models import User
from .models import Store


class StoreTests(APITestCase):
    def setUp(self):
        owner = User.objects.create_user(email='sade@example.com', username='sade', password='x')
        Store.objects.create(owner=owner, name='Sadé Atelier', slug='sade-atelier')
        self.user = User.objects.create_user(email='fatou@example.com', username='fatou', password='x')
        self.client.force_authenticate(self.user)

    def test_duplicate_name_gets_unique_slug(self):
        res = self.client.post('/api/stores/', {'name': 'Sadé Atelier'})
        self.assertEqual(res.status_code, 201, res.data)
        self.assertEqual(res.data['slug'], 'sade-atelier-2')

    def test_second_store_for_same_user_is_rejected_with_400(self):
        self.client.post('/api/stores/', {'name': 'Boutique Une'})
        res = self.client.post('/api/stores/', {'name': 'Boutique Deux'})
        self.assertEqual(res.status_code, 400)
