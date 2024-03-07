"""
Test for models.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):
    """Test for models."""

    def test_create_user_with_email_successfull(self):
        """Test for creating user with an email is successfull"""

        email = "test@example.com"
        password = "testing1q2w3e"
        user = get_user_model().objects.create_user(
            email = email,
            password = password,
        )

        self.assertEqual(user.email,email)
        self.assertTrue(user.check_password(password))