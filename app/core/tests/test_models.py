"""
    Test for models
"""
from django.urls import reverse
from django.test import TestCase

# Lấy model user để tạo user test
from django.contrib.auth import get_user_model

from core import models

# Dùng để lưu giá (price) của recipe với độ chính xác cao.
from decimal import Decimal

class ModelTests(TestCase):
    
    def setUp(self):
        """Create user and client."""
        self.admin_user = get_user_model().objects.create_superuser(
            email='admin@example.com',
            password='testpass123',
        )
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email='user@example.com',
            password='testpass123',
            name='Test User'
        )

    def test_create_user_with_email_successful(self):
        """Test creating a new user with an email is successful"""
        email = 'test@example.com'
        password = 'testpass123'

        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test email is normalized for new users."""
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@Example.Com', 'test4@example.com'],
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'sample123')
            self.assertEqual(user.email, expected)
            
    def test_new_user_without_email_raises_error(self):
        """Tests that creating a user without an email raises a value error."""
        with self.assertRaises(ValueError):
            # Gọi phương thức create_user để tạo user với email rỗng ('') và mật khẩu test123.
            get_user_model().objects.create_user('', 'test123')
            
    def test_create_superuser(self):
        """Test creating a super user."""
        # Mô phỏng việc tạo superuser để kiểm tra các thuộc tính is_superuser và is_staff.
        # superuser được phép đăng nhập và quản lý toàn bộ Django Admin.
        # get_user_model(): Lấy custom user model từ cấu hình AUTH_USER_MODEL.
        # Gọi phương thức create_superuser để tạo superuser 
        # với email test@example.com và mật khẩu test123.
        user = get_user_model().objects.create_superuser(
            'test@example.com', 'test123'
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
        
    def test_edit_user_page(self):
        """Test the edit user page works."""
        self.client.login(email='admin@example.com', password='test123')
        # Tạo URL mẫu /admin/core/user/<id>/change/ (theo cú pháp Django Admin).
        # Truyền ID của user
        # Ý nghĩa: Đảm bảo truy cập đúng trang chỉnh sửa của user cụ thể (ví dụ: /admin/core/user/1/change/).
        url = reverse('admin:core_user_change', args=[self.user.id])
        
        # Gửi yêu cầu GET đến URL bằng self.client (Django test client).
        response = self.client.get(url)
        
        # Kiểm tra mã trạng thái HTTP của phản hồi là 200 (OK).
        self.assertEqual(response.status_code, 200)
        
    def test_create_user_page(self):
        """Test the create user page works."""
        url = reverse('admin:core_user_add')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
        
        
    # Recipe
    def test_create_recipe(self):
        """Test creating a recipe is successful."""
        user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        recipe = models.Recipe.objects.create(
            user=user,
            title='Sample recipe name',
            time_minutes=5,
            price=Decimal('5.50'),
            description='Sample recipe description'
        )
        self.assertEqual(str(recipe), recipe.title)
        
    

