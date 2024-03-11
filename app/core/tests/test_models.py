"""
Test for models.
"""
from unittest.mock import patch
from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def create_user(**params):
    """create and return a new user"""
    return get_user_model().objects.create_user(**params)


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
        user = get_user_model().objects.create_user(
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

    def test_create_tag_success(self):
        """Test creating tag is sucessful."""
        user = create_user(email="test@example.com", password="test1q2w3e")
        tag = models.Tag.objects.create(user=user, name='Tag1')

        self.assertEqual(str(tag), tag.name)

    def test_create_ingredients_success(self):
        """Test creating ingredients is successful."""
        user = create_user(email="test@example.com", password="test1q2w3e")
        ingredient = models.Ingredient.objects.create(
            user=user,
            name='Ingredient 1',
        )

        self.assertEqual(str(ingredient), ingredient.name)

    @patch('core.models.uuid.uuid4')
    def test_recipe_file_name_uuid(self, mock_uuid):
        """Test generating image path."""
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_file_path(None, 'example.jpg')

        self.assertEqual(file_path, f'uploads/recipe/{uuid}.jpg')
