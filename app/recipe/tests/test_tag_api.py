"""
Test for Tag API
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Tag, Recipe
from recipe.serializers import TagSerializer

URL_TAGS = reverse("recipe:tag-list")


def detail_url(tag_id):
    """create n return tag detail url"""
    return reverse('recipe:tag-detail', args=[tag_id])


def create_user(**params):
    """create and return user."""
    return get_user_model().objects.create_user(**params)


class PublicTagApiTest(TestCase):
    """Test for unauthenticated API request."""

    def setUp(self) -> None:
        self.client = APIClient()

    def test_authentication_required(self):
        """Test for unauthenticated request."""
        res = self.client.get(URL_TAGS)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagApiTest(TestCase):
    """Test for authenticated API request."""

    def setUp(self) -> None:
        self.user = create_user(
            email='test@example.com',
            password='testing1q2w3e',
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test for retrieve list of tags request."""
        Tag.objects.create(user=self.user, name='Tag1')
        Tag.objects.create(user=self.user, name='Tag2')
        Tag.objects.create(user=self.user, name='Tag3')

        res = self.client.get(URL_TAGS)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tag_list_limited_to_current_user(self):
        """
        Test list of tags returned
        limited to current
        authenticated user
        """
        other_user = create_user(
            email="other@example.com",
            password="testing1q2w3e",
        )
        Tag.objects.create(user=other_user, name='other')
        tag = Tag.objects.create(user=self.user, name='Tag1')

        res = self.client.get(URL_TAGS)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)
        self.assertEqual(res.data[0]['id'], tag.id)

    def test_update_tags(self):
        """Test updating a tag"""
        tags = Tag.objects.create(user=self.user, name="Tag1")
        payload = {'name': 'Tag Update'}

        url = detail_url(tag_id=tags.id)

        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tags.refresh_from_db()
        self.assertEqual(tags.name, payload['name'])
        self.assertEqual(tags.user, self.user)

    def test_delete_tag(self):
        """Test to delete a tag."""
        tag = Tag.objects.create(user=self.user, name='Tag1')

        url = detail_url(tag.id)
        res = self.client.delete(url)
        # print(res.data)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        tags = Tag.objects.filter(user=self.user)
        self.assertFalse(tags.exists())

    def test_tags_assigned_to_recipe(self):
        """Test filtering tags assigned only to a recipe."""
        recipe1 = Recipe.objects.create(
            user=self.user,
            title='Nasi Goreng Mawut',
            time_minutes=15,
            price=Decimal('1.5'),
        )
        tag1 = Tag.objects.create(user=self.user, name='Nasi Goreng')
        tag2 = Tag.objects.create(user=self.user, name='Mie Goreng')
        recipe1.tags.add(tag1)

        res = self.client.get(URL_TAGS, {'assigned_only': 1})

        s1 = TagSerializer(tag1)
        s2 = TagSerializer(tag2)

        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filtered_tags_unique(self):
        """Test filtered tags return a unique list."""
        tag1 = Tag.objects.create(user=self.user, name='Nasi Goreng')
        Tag.objects.create(user=self.user, name='Mie Goreng')
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
        recipe1.tags.add(tag1)
        recipe2.tags.add(tag1)

        res = self.client.get(URL_TAGS, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)
