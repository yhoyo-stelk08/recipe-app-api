"""
Test for the Django admin modifications
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client


class AdminSiteTests(TestCase):
    """Test for django admin page."""

    def setUp(self):
        """create user and client."""

        self.user = Client
        self.admin_user = get_user_model().objects.create_superuser(
            email='administrator@example.com',
            password="testing1q2w3e",
        )
        self.client.force_login(self.admin_user)

        self.user = get_user_model().objects.create_user(
            email="user@example.com",
            password="testing1q2w3e",
            name="Test Users",
        )

    def test_users_list(self):
        """Test that users are listed on the page."""
        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)

        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_user_edit_page(self):
        """Test user edit page if working correctly."""
        url = reverse('admin:core_user_change', args=[self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_user_add_page(self):
        """Test user add page if working correctly."""
        url = reverse('admin:core_user_add')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
