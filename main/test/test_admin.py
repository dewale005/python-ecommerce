from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

class AdminSiteTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.admin_user = get_user_model().object.create_superuser(
            email='admin@test.com', password='test123456'
        )
        self.client.force_login(self.admin_user)
        self.user = get_user_model().object.create_user(
            email='test@test.com', password='test123456', name='test user'
        )

    def test_users_listed(self):
        """Test that users are listed on user page"""

        url = reverse('admin:main_user_changelist')
        res = self.client.get(url)

        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_user_change_page(self):
        """Test that the user edit page works"""
        url = reverse('admin:main_user_change', args=[self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        """Test that the create user page works"""
        url = reverse('admin:main_user_add')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
