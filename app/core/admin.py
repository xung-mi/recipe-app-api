# core/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

class UserAdmin(BaseUserAdmin):
    ordering = ['email'] # Giúp sắp xếp user theo email, cải thiện khả năng tìm kiếm và quản lý.
    list_display = ['email', 'name'] # Giới hạn các trường hiển thị (ví dụ: không hiển thị mật khẩu mã hóa) để giao diện rõ ràng và hữu ích hơn.
    fieldsets = ( # Cấu hình bố cục của trang chỉnh sửa (edit page), nhóm các trường liên quan logic với nhau.
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('name',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',), # Áp dụng CSS class để điều chỉnh trường rộng hơn
            'fields': ('email', 'password1', 'password2', 'name', 'is_active', 'is_staff', 'is_superuser'), # Cấu hình bố cục của trang thêm mới, 
                                                           #password2 (hỗ trợ xác nhận mật khẩu).
        }),
    )
    readonly_fields = ['last_login'] # Chỉ định các trường chỉ đọc

admin.site.register(User, UserAdmin)