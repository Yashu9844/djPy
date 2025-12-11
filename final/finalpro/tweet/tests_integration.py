from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from .models import Tweet
import json


class APIIntegrationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", email="test@test.com", password="testpass123")
        self.token = Token.objects.create(user=self.user)

    # Registration API Tests
    def test_register_api_success(self):
        url = reverse('api_register')
        data = {
            'username': 'newuser',
            'email': 'new@test.com',
            'password': 'newpass123',
            'password2': 'newpass123'
        }
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertIn('token', response.json())
        self.assertIn('user', response.json())
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_register_api_password_mismatch(self):
        url = reverse('api_register')
        data = {
            'username': 'baduser',
            'email': 'bad@test.com',
            'password': 'pass123456',
            'password2': 'different'
        }
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('password2', response.json())

    def test_register_api_duplicate_username(self):
        url = reverse('api_register')
        data = {
            'username': 'testuser',  # Already exists
            'email': 'another@test.com',
            'password': 'pass123456',
            'password2': 'pass123456'
        }
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    # Login API Tests
    def test_login_api_success(self):
        url = reverse('api_login')
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.json())
        self.assertIn('user', response.json())
        self.assertEqual(response.json()['user']['username'], 'testuser')

    def test_login_api_invalid_credentials(self):
        url = reverse('api_login')
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_login_api_nonexistent_user(self):
        url = reverse('api_login')
        data = {
            'username': 'nouser',
            'password': 'somepass'
        }
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    # Logout API Tests
    def test_logout_api_authenticated(self):
        url = reverse('api_logout')
        response = self.client.post(url, HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Token.objects.filter(user=self.user).exists())

    def test_logout_api_unauthenticated(self):
        url = reverse('api_logout')
        response = self.client.post(url)
        self.assertIn(response.status_code, (400, 401, 403))

    # Current User API Tests
    def test_current_user_authenticated(self):
        url = reverse('api_current_user')
        response = self.client.get(url, HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['username'], 'testuser')

    def test_current_user_unauthenticated(self):
        url = reverse('api_current_user')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)

    # Frontend View Tests
    def test_api_feed_page_loads(self):
        url = reverse('tweet_list_api')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'API-Powered')
        self.assertContains(response, 'api.js')

    def test_login_api_page_loads(self):
        url = reverse('login_api')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sign in to TweetBar')

    def test_register_api_page_loads(self):
        url = reverse('register_api')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create your TweetBar account')

    # Full Flow Test
    def test_full_registration_login_tweet_flow(self):
        # 1. Register
        register_url = reverse('api_register')
        register_data = {
            'username': 'flowuser',
            'email': 'flow@test.com',
            'password': 'flowpass123',
            'password2': 'flowpass123'
        }
        reg_response = self.client.post(register_url, json.dumps(register_data), content_type='application/json')
        self.assertEqual(reg_response.status_code, 201)
        token = reg_response.json()['token']
        
        # 2. Create tweet
        tweet_url = reverse('tweet-list')
        tweet_data = {'text': 'My first API tweet!'}
        tweet_response = self.client.post(
            tweet_url,
            json.dumps(tweet_data),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Token {token}'
        )
        self.assertEqual(tweet_response.status_code, 201)
        tweet_id = tweet_response.json()['id']
        
        # 3. Retrieve tweet
        detail_url = reverse('tweet-detail', args=[tweet_id])
        detail_response = self.client.get(detail_url)
        self.assertEqual(detail_response.status_code, 200)
        self.assertEqual(detail_response.json()['text'], 'My first API tweet!')
        
        # 4. Update tweet
        update_data = {'text': 'Updated via API!'}
        update_response = self.client.patch(
            detail_url,
            json.dumps(update_data),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Token {token}'
        )
        self.assertEqual(update_response.status_code, 200)
        
        # 5. Delete tweet
        delete_response = self.client.delete(detail_url, HTTP_AUTHORIZATION=f'Token {token}')
        self.assertEqual(delete_response.status_code, 204)
        self.assertFalse(Tweet.objects.filter(id=tweet_id).exists())
