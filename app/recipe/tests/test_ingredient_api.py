"""
Test Ingredients API
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import (
    Recipe,
    Ingredient,
)

from recipe.serializers import IngredientSerializer

INGREDIENT_URL = reverse('recipe:ingredient-list')


def create_user(email="test@example.com", password="testing1q2w3e"):
    """helper function to create and return user."""
    return get_user_model().objects.create_user(email=email, password=password)


def create_ingredient(user, **params):
    """helper function to create and return ingredient."""
    default = {
        'name': 'Ingredients 1 ',
    }
    default.update(params)
    ingredient = Ingredient.objects.create(user=user, **default)
    return ingredient


class PublicIngredientsApiTest(TestCase):
    """Test for unauthenticated request."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test authentication is required for request."""
        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTest(TestCase):
    """Test for authenticated request"""

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_retrieving_ingredient(self):
        """Test for retrieving list of ingredients."""
        create_ingredient(user=self.user, name='Salt')
        create_ingredient(user=self.user, name='Pepper')

        res = self.client.get(INGREDIENT_URL)

        ingredients = Ingredient.objects.all().order_by('name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_current_user(self):
        """Test ingredients return only to current user"""
        other_user = create_user(email="other@example.com")
        create_ingredient(user=other_user, name='Salt')
        ingredient = create_ingredient(user=self.user, name='Pepper')

        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)
        self.assertEqual(res.data[0]['id'], ingredient.id)
