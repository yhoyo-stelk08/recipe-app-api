"""
Test Ingredients API
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import (
    Ingredient,
    Recipe,
)

from recipe.serializers import IngredientSerializer

INGREDIENT_URL = reverse('recipe:ingredient-list')


def detail_url(ingredient_id):
    """Helper function to create and return detail ingredient."""
    return reverse('recipe:ingredient-detail', args=[ingredient_id])


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
        # print(res.data)
        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)
        # print(serializer.data)

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

    def test_update_ingredients(self):
        """Test update ingredient."""
        ingredient = create_ingredient(user=self.user, name='Salt')

        payload = {
            'name': 'Pepper',
        }
        url = detail_url(ingredient_id=ingredient.id)
        res = self.client.patch(url, payload)
        # print(res.data['name'])

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingredient.refresh_from_db()
        self.assertEqual(res.data['name'], payload['name'])
        self.assertEqual(ingredient.name, payload['name'])
        self.assertEqual(ingredient.user, self.user)

    def test_delete_ingredients(self):
        """Test delete ingredient."""
        ingredient = create_ingredient(user=self.user, name='Salt')
        url = detail_url(ingredient_id=ingredient.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        ingredient = Ingredient.objects.filter(user=self.user)
        # print(ingredient)
        self.assertEqual(len(ingredient), 0)
        self.assertFalse(ingredient.exists())

    def test_ingredients_assign_to_recipe(self):
        """Test filtering ingredients assign to a recipe."""
        recipe1 = Recipe.objects.create(
            user=self.user,
            title='Mie Goreng Jawa',
            time_minutes=20,
            price=Decimal('2.99'),
        )
        ingredient1 = create_ingredient(user=self.user, name='Mie')
        ingredient2 = create_ingredient(user=self.user, name='Wortel')
        recipe1.ingredients.add(ingredient1)

        res = self.client.get(INGREDIENT_URL, {'assigned_only': 1})

        s1 = IngredientSerializer(ingredient1)
        s2 = IngredientSerializer(ingredient2)

        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filtered_ingredients_unique(self):
        """Test filtered ingredients return a unique list."""
        ingredient1 = Ingredient.objects.create(user=self.user, name='Eggs')
        Ingredient.objects.create(user=self.user, name='Lentils')
        recipe1 = Recipe.objects.create(
            user=self.user,
            title='Telur orak arik',
            time_minutes=5,
            price=Decimal('0.5'),
        )
        recipe2 = Recipe.objects.create(
            user=self.user,
            title='Telur mata sapi',
            time_minutes=5,
            price=Decimal('0.5'),
        )
        recipe1.ingredients.add(ingredient1)
        recipe2.ingredients.add(ingredient1)

        res = self.client.get(INGREDIENT_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)
