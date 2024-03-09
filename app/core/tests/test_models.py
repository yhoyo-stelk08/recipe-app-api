"""
Test for models.
"""
from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


class ModelTests(TestCase):
    """Test for models."""

    def test_create_user_with_email_successfull(self):
        """Test for creating user with an email is successfull"""

        email = "test@example.com"
        password = "testing1q2w3e"
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_is_normalized(self):
        """Test for new user email is normalized or not."""
        email_sample_list = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['TEST2@EXAMPLE.COM', 'TEST2@example.com'],
            ['test3@Example.com', 'test3@example.com'],
            ['Test4@example.COM', 'Test4@example.com'],
            ['test5@example.Com', 'test5@example.com'],
        ]

        for email, expected in email_sample_list:
            user = get_user_model().objects.create_user(email, 'testing1q2w3e')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test for new user without an email will raise error."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'testing1q2w3e')

    def test_create_superuser_successfully(self):
        """Test for create superuser successfully"""
        email = "admin@example.com"
        password = "adminpass1q2w3e"

        user = get_user_model().objects.create_superuser(
            email=email,
            password=password,
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.check_password(password))

    def test_create_recipe(self):
        """Test creating a recipe is successful."""
        user = get_user_model().create_user(
            email='test@example.com',
            password='testing1q2w3e',
        )

        recipe = models.Recipe.objects.create(
            user=user,
            title='Sampe Recipe Name',
            time_minutes=5,
            price=Decimal('5.50'),
            desc='Sample recipe description',
        )

        self.assertEqual(str(recipe), recipe.title)
