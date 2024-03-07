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
