from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token' )

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
