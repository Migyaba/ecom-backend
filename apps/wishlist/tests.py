from rest_framework.test import APITestCase

from apps.users.models import User


class WishlistTests(APITestCase):
    def test_unknown_product_is_rejected_with_400(self):
        self.client.force_authenticate(User.objects.create_user(email='fatou@example.com', username='fatou', password='x'))
        res = self.client.post('/api/wishlist/', {'product_id': 9999}, format='json')
        self.assertEqual(res.status_code, 400)
