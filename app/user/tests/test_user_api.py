# user/tests/test_user_api.py
"""Tests for the user API."""

# Base class cho unit tests.
from django.test import TestCase

# Lấy custom user model (User).
from django.contrib.auth import get_user_model

# Tạo URL từ tên view (URL name).
from django.urls import reverse

# Client để gửi yêu cầu HTTP trong test.
from rest_framework.test import APIClient

# Cung cấp mã trạng thái HTTP (ví dụ: status.HTTP_201_CREATED).
from rest_framework import status

# Định nghĩa hằng số URL cho endpoint /user/create/ bằng reverse
# user:create: Tên URL (namespace user, view create)
# Ý nghĩa: Sử dụng hằng số để tái sử dụng URL trong các test, tránh hardcode, giúp truy cập endpoint dễ dàng và linh hoạt nếu URL thay đổi.
CREATE_USER_URL = reverse('user:create')

from rest_framework.test import APITestCase

# Tạo URL từ tên view (URL name).
# reverse được dùng để lấy URL tương ứng với một tên route (URL name) đã được định nghĩa trong file urls.py.
# Trả về một chuỗi URL (ví dụ: '/api/user/token/').
token_url = reverse('user:token')

# lấy URL của endpoint /me/
me_url = reverse('user:me')

def create_user(**params):
    """Create and return a new user."""
    # Tái sử dụng logic tạo user, tránh lặp code trong các test.
    return get_user_model().objects.create_user(**params) 


class PublicUserAPITests(TestCase):
    """Test the public features of the user API."""
    
    # Phương thức chạy trước mỗi test để thiết lập môi trường
    def setUp(self):
        # Tạo instance của APIClient để gửi yêu cầu HTTP.
        # Đảm bảo mỗi test có client riêng để gửi yêu cầu tới API.
        self.client = APIClient()
        self.user_details = {
            'name': 'test name',
            'email': 'test@example.com',
            'password': 'testpythonuserpassword123'
        }
        self.create_user = get_user_model().objects.create_user
        
    # Test kiểm tra tạo user thành công qua endpoint /user/create/.
    def test_create_user_success(self):
        """Test creating a user is successful."""
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test Name',
        }
        
        # Gửi yêu cầu POST đến CREATE_USER_URL với payload
        res = self.client.post(CREATE_USER_URL, payload)
        
        # Kiểm tra mã trạng thái phản hồi là 201 Created (thành công khi tạo tài nguyên).
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        
        # Lấy user từ database dựa trên email trong payload
        # Để kiểm tra user đã thực sự được tạo trong database.
        user = get_user_model().objects.get(email=payload['email'])
        
        # Gọi check_password để kiểm tra mật khẩu trong payload khớp với mật khẩu đã mã hóa của user.
        self.assertTrue(user.check_password(payload['password']))
        
        # Kiểm tra mật khẩu không được trả về trong phản hồi
        self.assertNotIn('password', res.data)
        
    # Test lỗi khi email đã tồn tại
    def test_user_with_email_exists_error(self):
        """Test error returned if user with email exists."""
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test Name',
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)
        
        # Mã 400 là chuẩn REST cho lỗi dữ liệu không hợp lệ.
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        
    # Test lỗi khi mật khẩu quá ngắn
    def test_password_too_short_error(self):
        """Test an error is returned if password less than 5 chars."""
        payload = {
            'email': 'test@example.com',
            'password': 'pw',
            'name': 'Test Name',
        }
        res = self.client.post(CREATE_USER_URL, payload)
        
        # Xác nhận API từ chối do mật khẩu không đạt yêu cầu.
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Xác nhận user không được tạo khi yêu cầu bị từ chối.
        user_exists = get_user_model().objects.filter(email=payload['email']).exists()
        
        # Đảm bảo database không bị thay đổi khi yêu cầu không hợp lệ.
        self.assertFalse(user_exists)
        
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
        
    def test_retrieve_user_unauthorized(self):
        """Test authentication is required for users."""
        res = self.client.get(me_url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

# Tách biệt test không xác thực (public) và xác thực (private).
class PrivateUserAPITests(TestCase):
    """Test API requests that require authentication."""
    # Xử lý xác thực trong setUp để tránh lặp code.
    def setUp(self):
        self.user = create_user(
            email='test@example.com',
            password='testpass123',
            name='test name'
        )
        self.client = APIClient()
        
        # Giả lập xác thực cho user, tránh test hệ thống xác thực thực tế.
        self.client.force_authenticate(user=self.user)
        
    # Test 1: Truy xuất profile thành công
    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged-in user."""
        res = self.client.get(me_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email
        })
        
    # Test 2: Không cho phép POST
    def test_post_me_not_allowed(self):
        """Test POST is not allowed for the endpoint."""
        res = self.client.post(me_url, {})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        
    # Test 3: Cập nhật profile
    def test_update_user_profile(self):
        """Test updating the user profile for the authenticated user."""
        payload = {'name': 'updated name', 'password': 'newpassword123'}
        # Gửi PATCH request đến /me/ với payload cập nhật name và password.
        res = self.client.patch(me_url, payload)\
        # cập nhật dữ liệu user từ database.
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        
    
        
    
    
    
        
        
    
    