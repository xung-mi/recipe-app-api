"""
    Test for models
"""

from django.test import TestCase
# allows us to get the user model that is currently active in this project
from django.contrib.auth import get_user_model

from core import models

class ModelTests(TestCase):
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

