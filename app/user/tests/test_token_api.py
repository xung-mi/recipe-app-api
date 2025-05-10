from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

# Tạo URL từ tên view (URL name).
# reverse được dùng để lấy URL tương ứng với một tên route (URL name) đã được định nghĩa trong file urls.py.
# Trả về một chuỗi URL (ví dụ: '/api/user/token/').
token_url = reverse('user:token')

class TokenAPITests(APITestCase):
    """Test cases for Token API."""

    def setUp(self):
        """Set up common data for all tests."""
        self.user_details = {
            'name': 'test name',
            'email': 'test@example.com',
            'password': 'testpythonuserpassword123'
        }
        self.create_user = get_user_model().objects.create_user

    def test_create_token_for_user(self):
        """Test generates token for valid credentials."""
        self.create_user(**self.user_details)
        payload = {
            'email': self.user_details['email'],
            'password': self.user_details['password']
        }
        res = self.client.post(token_url, payload)
        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_bad_credentials(self):
        """Test returns error if credentials invalid."""
        self.create_user(email='test@example.com', password='goodpass')
        payload = {
            'email': 'test@example.com',
            'password': 'badpass'
        }
        res = self.client.post(token_url, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_password(self):
        """Test posting a blank password returns an error."""
        self.create_user(email='test@example.com', password='goodpass')  # Thêm user để đảm bảo tính nhất quán
        payload = {
            'email': 'test@example.com',
            'password': ''
        }
        res = self.client.post(token_url, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)