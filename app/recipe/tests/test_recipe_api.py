"""
Test recipe API
"""
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import (
    Recipe,
    Tag,
    Ingredient,
)
from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer,
)


RECIPE_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    """return recipe detail url"""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def create_recipe(user, **params):
    """Create and return a sample recipe"""
    defaults = {
        'title': 'Sample Recipe',
        'desc': 'Sample recipe descriptions',
        'time_minutes': 11,
        'price': Decimal('5.11'),
        'link': 'http://example.com/',
    }
    defaults.update(params)

    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe


def create_user(**params):
    """Create and return user"""
    return get_user_model().objects.create_user(**params)


class PublicRecipeApiTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API."""
        res = self.client.get(RECIPE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='test@example.com',
            password='testing1q2w3e',
            name='Test User',
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test retrieving list of recipes."""
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipe_list_limited_to_current_user(self):
        """
        Test list of recipes returned
        limited to current
        authenticated user
        """
        other_user = create_user(
            email="other@example.com",
            password="other1q2w3e"
        )
        create_recipe(user=other_user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)

        recipe = Recipe.objects.filter(user=self.user).order_by('-id')
        serializer = RecipeSerializer(recipe, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(len(res.data), 1)

    def test_retrieve_detail_recipe(self):
        """Test retrieving recipe details"""
        recipe = create_recipe(user=self.user)

        url = detail_url(recipe.id)

        res = self.client.get(url)
        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe(self):
        """Test creating a recipe."""
        payload = {
            'title': 'Sample Recipe',
            'time_minutes': 30,
            'price': Decimal('2.34'),
        }
        res = self.client.post(RECIPE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)

    def test_partial_update(self):
        """Test partial update a recipe."""
        original_desc = "Recipe Original Description"
        recipe = create_recipe(
            user=self.user,
            title='Sample Recipe',
            desc=original_desc,
        )
        payload = {'title': 'New Title'}
        url = detail_url(recipe_id=recipe.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.desc, original_desc)
        self.assertEqual(recipe.user, self.user)

    def test_full_update(self):
        """Test full update of recipe."""
        recipe = create_recipe(
            user=self.user,
            title='Sample Recipe Title',
            time_minutes=22,
            price=Decimal('4.99'),
            desc='Test Description Recipe',
            link='http://example.com/recipe.pdf',
        )

        payload = {
            'user': self.user,
            'title': 'Sample Recipe Title Updated',
            'time_minutes': 21,
            'price': Decimal('5.99'),
            'desc': 'Test Description Recipe Updated',
            'link': 'http://example.com/recipe_update.pdf',
        }

        url = detail_url(recipe_id=recipe.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)

    def test_delete_recipe(self):
        """Test deleting a recipe."""
        recipe = create_recipe(
            user=self.user,
            title='Sample Recipe Title',
            time_minutes=22,
            price=Decimal('4.99'),
            desc='Test Description Recipe',
            link='http://example.com/recipe.pdf',
        )
        url = detail_url(recipe_id=recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

    def test_another_user_delete_recipe_error(self):
        """Test user delete another user recipe gives error."""
        other_user = create_user(
            email='other@example.com',
            password='othertest1q2w3e',
        )
        recipe = create_recipe(user=other_user)
        url = detail_url(recipe_id=recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())

    def test_create_recipe_with_new_tags(self):
        """Test create recipe with new tags"""
        payload = {
            'title': 'Nasi Goreng',
            'time_minutes': 30,
            'price': Decimal('1.99'),
            'tags': [{'name': 'Nasi'}, {'name': 'Makan siang'}],
        }
        res = self.client.post(RECIPE_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)
        for tag in payload['tags']:
            exists = recipe.tags.filter(
                name=tag['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_existing_tags(self):
        """Test create recipe with the existing tags."""
        tag1 = Tag.objects.create(user=self.user, name='Indonesia')
        payload = {
            'title': 'Nasi Goreng',
            'time_minutes': 30,
            'price': Decimal('1.99'),
            'tags': [{'name': 'Indonesia'}, {'name': 'Makan siang'}],
        }
        res = self.client.post(RECIPE_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        # self.assertEqual(recipe.tags.name, tag1.name)
        self.assertEqual(recipe.tags.count(), 2)
        self.assertIn(tag1, recipe.tags.all())
        for tag in payload['tags']:
            exists = recipe.tags.filter(
                name=tag['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_tag_on_update(self):
        """Test creating tag when updating an existing recipe."""
        recipe = create_recipe(user=self.user)

        payload = {
            'tags': [{'name': 'Lunch'}],
        }
        url = detail_url(recipe_id=recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_tag = Tag.objects.get(user=self.user, name='Lunch')
        self.assertIn(new_tag, Tag.objects.all())

    def test_update_tag_on_update(self):
        """Test updating tag when updating a recipe."""
        tag_breakfast = Tag.objects.create(user=self.user, name='Breakfast')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag_breakfast)

        tag_lunch = Tag.objects.create(user=self.user, name='Lunch')
        payload = {'tags': [{'name': 'Lunch'}]}
        url = detail_url(recipe_id=recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(tag_lunch, recipe.tags.all())
        self.assertNotIn(tag_breakfast, recipe.tags.all())

    def test_clearing_recipe_tags(self):
        """Test clearing a recipe tags."""
        recipe = create_recipe(user=self.user)
        tag = Tag.objects.create(user=self.user, name='Dessert')
        recipe.tags.add(tag)  # adding tags into new created recipe
        payload = {
            'tags': []
        }
        url = detail_url(recipe_id=recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.tags.count(), 0)

    def test_create_recipe_with_new_ingredients(self):
        """Test creating recipe with new ingredients."""
        payload = {
            'title': 'Nasi Goreng',
            'time_minutes': 20,
            'price': Decimal('1.99'),
            'ingredients': [{'name': 'Salt'}, {'name': 'Pepper'}]
        }
        res = self.client.post(RECIPE_URL, payload, format='json')
        # print(res.data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.ingredients.count(), 2)
        for ingredient in payload['ingredients']:
            exists = recipe.ingredients.filter(
                name=ingredient['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_existing_ingredients(self):
        """Test creating a recipe with existing ingredients."""
        ingredient1 = Ingredient.objects.create(user=self.user, name='Salt')
        payload = {
            'title': 'Nasi Goreng',
            'time_minutes': 15,
            'price': Decimal('1.99'),
            'ingredients': [{'name': 'Salt'}, {'name': 'Pepper'}],
        }
        res = self.client.post(RECIPE_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.ingredients.count(), 2)
        self.assertIn(ingredient1, recipe.ingredients.all())
        for ingredient in payload['ingredients']:
            exists = recipe.ingredients.filter(
                name=ingredient['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_ingredients_on_update(self):
        """Test updating a recipe ingredients wih new created ingredients."""
        recipe = create_recipe(user=self.user)

        payload = {
            'ingredients': [
                {'name': 'Salt'},
            ]
        }
        url = detail_url(recipe_id=recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_ingredients = Ingredient.objects.get(user=self.user, name='Salt')
        self.assertIn(new_ingredients, Ingredient.objects.all())

    def test_update_ingredients_on_update(self):
        """Test updating a recipe ingredients with an existing ingredients"""
        salt = Ingredient.objects.create(user=self.user, name='Salt')
        recipe = create_recipe(user=self.user)
        recipe.ingredients.add(salt)

        pepper = Ingredient.objects.create(user=self.user, name='Pepper')
        payload = {
            'ingredients': [
                {'name': 'Pepper'},
            ],
        }
        url = detail_url(recipe_id=recipe.id)
        res = self.client.patch(url, payload, format='json')
        # print(res.data)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(pepper, recipe.ingredients.all())
        self.assertNotIn(salt, recipe.ingredients.all())

    def test_clearing_recipe_ingredients(self):
        """Test clearing a recipe ingredients."""
        recipe = create_recipe(user=self.user)
        ingredient = Ingredient.objects.create(user=self.user, name='Salt')
        recipe.ingredients.add(ingredient)

        payload = {
            'ingredients': []
        }
        url = detail_url(recipe_id=recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.ingredients.count(), 0)
