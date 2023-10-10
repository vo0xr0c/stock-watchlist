"""
Basic tests for the API endpoints.
"""
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import User, Security, Watchlist


class ViewsTestCases(APITestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create(username='testuser', password='testpassword')

        # Create test stocks
        self.apple = Security.objects.create(ticker='AAPL', name='Apple')
        self.google = Security.objects.create(ticker='GOOG', name='Google')

        # Create a watchlist entry
        Watchlist.objects.create(user=self.user, stock=self.apple)

    def test_login_user(self):
        url = reverse('login')
        data = {'username': 'testuser'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')

    def test_list_securities(self):
        url = reverse('security-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_retrieve_security(self):
        url = reverse('security-detail', args=[self.apple.ticker])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['ticker'], self.apple.ticker)

    def test_list_watchlist(self):
        url = reverse('watchlist-list')
        self.client.credentials(HTTP_Username='testuser')  # Mock authentication
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_add_to_watchlist(self):
        url = reverse('watchlist-list')
        data = {'ticker': self.google.ticker}
        self.client.credentials(HTTP_Username='testuser')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_remove_from_watchlist(self):
        url = reverse('watchlist-detail', args=[self.apple.ticker])
        self.client.credentials(HTTP_Username='testuser')
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def tearDown(self):
        self.user.delete()
