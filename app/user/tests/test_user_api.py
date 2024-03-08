"""
Test for user API.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


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
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)
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

    def test_create_token_for_user(self):
        """Test generate token for valid credentials."""
        user_details = {
            'email': 'test@example.com',
            'name': 'Test User',
            'password': 'testing1q2w3e',
        }

        create_user(**user_details)

        payload = {
            'email': user_details['email'],
            'password': user_details['password'],
        }

        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_bad_credential(self):
        """Test return error if creadential is invalid."""
        create_user(email="test@example.com", password='goodpassword')

        payload = {'email': 'test@example.com', 'password': 'badpassword'}

        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_password(self):
        """Test return error if password is blank."""
        payload = {'email': 'test@example.com', 'password': ''}

        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthorized_user(self):
        """Test authentication required for users."""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUseerApiTests(TestCase):
    """Test the private features of the user api
    that require authentication."""

    def setUp(self):
        self.user = create_user(
            email='test@example.com',
            password='testing1q2w3e',
            name="Test User"
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_user_profile_success(self):
        """Test retrieving profile for logged in users."""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email,
        })

    def test_post_method_not_allowed_for_me(self):
        """Test for post method not allowed for this endpoint"""
        # self.client.force_authenticate(user=get_user_model().objects.create_user(email='test@example.com', password='testing1q2w3e'))
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test for updating user data in profile
        for authenticated users. """
        payload = {
            'name': 'New Test Name',
            'password': 'newpassword1q2w3e',
        }

        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
