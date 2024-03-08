"""
Test for user API.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')


def create_user(**params):
    """Create and return user"""
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test the public features of the user api"""

    def setUp(self):
        self.client = APIClient()

    def test_create_user(self):
        """Test creating a user is successful."""
        payload = {
            'email': 'test@example.com',
            'password': 'testing1q2w3e',
            'name': 'Test User',
        }
        res = self.client.post(CREATE_USER_URL, payload)

        # check if the response status code is equals HTTP_201_CREATED
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        # get user email and assign it into user variable
        user = get_user_model().objects.get(email=payload['email'])
        # check if the password is according to password criteria
        self.assertTrue(user.check_password(payload['password']))
        # check if the password is not in the data passing back to user
        self.assertNotIn('password', res.data)

    def test_user_with_email_exists_error(self):
        """Test error returned if user with the email
        are already exists in database"""
        payload = {
            'email': 'test@example.com',
            'password': 'testing1q2w3e',
            'name': 'Test User',
        }

        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)

        # Test if the user already exists in database , it will return an error
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """Test an error is returned when password is less than 5 chars."""
        payload = {
            'email': 'test@example.com',
            'password': 'test',
            'name': 'Test user',
        }

        res = self.client.post(CREATE_USER_URL, payload)

        # print(res.data)
        # print(res.data.get('password'))

        # Test if the password is too short, it will return an error
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)
