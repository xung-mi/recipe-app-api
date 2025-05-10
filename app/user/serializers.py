"""
    Serializer là cầu nối giữa dữ liệu thô (JSON từ request) và model trong cơ sở dữ liệu.
    Lấy input từ API và validate input, đảm bảo input bảo mật và chính xác
"""

from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers

from django.utils.translation import gettext as _

class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        # Lấy model người dùng tùy chỉnh.
        model = get_user_model() 
        # Chỉ định các trường cho phép trong API (email, password, name).
        fields = ("email", "password", "name")
        # Đặt password là write_only (không trả về trong response) và yêu cầu độ dài tối thiểu 5 ký tự.
        extra_kwargs = {"password": {"write_only": True, "min_length": 5}}

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        return get_user_model().objects.create_user(**validated_data)
    
    # Ghi đè phương thức update để tùy chỉnh cập nhật user.
    def update(self, instance, validated_data):
        """Update and return user."""
        password = validated_data.pop('password', None)
        
        # Gọi super().update để cập nhật các trường khác (email, name).
        user = super().update(instance, validated_data)
        if password:
            # gọi set_password để mã hóa và lưu user.
            user.set_password(password)
            user.save()
        return user
    
    
    

class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user auth token."""
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        """Validate and authenticate the user."""
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(
            request=self.context.get('request'),
            username=email,  # Sử dụng email làm username
            password=password
        )
        if not user:
            msg = _('Unable to authenticate with provided credentials')
            raise serializers.ValidationError(msg, code='authorization')
        attrs['user'] = user
        return attrs
