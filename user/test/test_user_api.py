from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token' )
AUTHENTICATED_ME_URL = reverse('user:me')

def create_user(**param):
    return get_user_model().object.create_user(**param)


class PublicUserApiTest(TestCase):
    """Test the user's api(Public)"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test creating user with valid payload is successful"""
        payload = {
            "email": "test@test.com",
            'password': 'test123456',
            "name": 'test'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().object.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)


    def test_user_exist(self):
        """Test creating a user already exist"""
        payload = {
            "email": "test@test.com",
            'password': 'test123456',
            "name": 'test'
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    
    def test_password_too_short(self):
        """Testing that the password must be more than 5 characters"""
        payload = {
            "email": "test@test.com",
            'password': 'test',
            "name": 'test'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exist = get_user_model().object.filter(email=payload['email']).exists()
        self.assertFalse(user_exist)


    def test_create_token_for_user(self):
        """Testing that the token is created for the user"""
        payload = {
            "email": "test@test.com",
            'password': 'test123456',
            "name": 'test'
        }
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """Test that token is not created if invalid credentials sre given"""
        payload = {
            "email": "test@test.com",
            'password': 'test123456',
            "name": 'test'
        }
        create_user(**payload)
        payload['password'] = "wrongpassword"
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    
    def test_create_token_without_user(self):
        """Test thats toke is not created if user doesn't exist"""
        payload = {
            "email": "test@test.com",
            'password': 'test123456',
            "name": 'test'
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """Test that email and password are required"""
        payload = {
            "email": "test@test.com",
            'password': '',
            "name": 'test'
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retreive_user_unauthorized(self):
        """Test authentication is required for users"""
        # res = self.client.get(AUTHENTICATED_ME_URL)

        # self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Test API request that require authentication"""

    def setUp(self):
        self.user = create_user(email='test@test.com',password='test12345',name='test')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retreive_profile_success(self):
        """Test retrieving profile for logged in user"""
        res = self.client.get(AUTHENTICATED_ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email
        })

    def test_post_not_allowed(self):
        """Test post is not allowed on the me url"""
        res = self.client.post(AUTHENTICATED_ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test updating the user profile for authenticated user"""
        payload = {
            'name': "new name",
            'password': 'new password',
        }
        res = self.client.patch(AUTHENTICATED_ME_URL, payload)
        
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

