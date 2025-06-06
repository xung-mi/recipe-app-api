from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# import đối tượng settings, cho phép truy cập các cấu hình của dự án được định nghĩa trong file settings.py
from django.conf import settings

# AbstractBaseUser cung cấp chức năng xác thực nhưng không có trường mặc định
# PermissionsMixin thêm chức năng quản lý quyền và các trường liên quan.
# Email được dùng làm trường xác thực duy nhất
# UserManager cho phép linh hoạt tạo user với các trường bổ sung qua extra_fields.
# Mã hóa mật khẩu bảo vệ thông tin người dùng, tuân theo best practices.


class UserManager(BaseUserManager):
    """Manager for users"""
    
    def create_user(self, email, password=None, **extra_fields):
        """Create and save a new user"""
        # Kiểm tra nếu email rỗng (''), None, hoặc bất kỳ giá trị falsy nào.
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password) # set_password là một phương thức của BaseUserManager để mã hóa password
        user.save(using=self._db) # lưu user vào database
        return user\

    def create_superuser(self, email, password):
        """Create and return a new superuser."""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

#Tạo Custom User Model
class User(AbstractBaseUser, 
           PermissionsMixin):
    """Custom user model that supports using email instead of username"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email' #dùng email thay vì username mặc định cho xác thực.
    
class Recipe(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, # dùng import settings.AUTH_USER_MODEL để tránh hardcode, tái sử dụng, dễ thay đổi
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    time_minutes = models.IntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    link = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.title