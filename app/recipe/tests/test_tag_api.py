"""
Test for Tag API
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core import models
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
        models.Tag.objects.create(user=self.user, name='Tag1')
        models.Tag.objects.create(user=self.user, name='Tag2')
        models.Tag.objects.create(user=self.user, name='Tag3')

        res = self.client.get(URL_TAGS)

        tags = models.Tag.objects.all().order_by('-name')
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
        models.Tag.objects.create(user=other_user, name='other')
        tag = models.Tag.objects.create(user=self.user, name='Tag1')

        res = self.client.get(URL_TAGS)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)
        self.assertEqual(res.data[0]['id'], tag.id)

    def test_update_tags(self):
        """Test updating a tag"""
        tags = models.Tag.objects.create(user=self.user, name="Tag1")
        payload = {'name': 'Tag Update'}

        url = detail_url(tag_id=tags.id)

        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tags.refresh_from_db()
        self.assertEqual(tags.name, payload['name'])
        self.assertEqual(tags.user, self.user)
