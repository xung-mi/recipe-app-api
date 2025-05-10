"""Views for the user API."""
from user.serializers import UserSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from rest_framework import generics, authentication, permissions
from user.serializers import UserSerializer, AuthTokenSerializer

"""
    CreateUserView là một class-based view trong DFR
    xử lý yêu cầu HTTP POST => create new user object trong database
    Chỉ cần truyền vào module serializer. 
    APIView tạo object dựa trên Meta class đã defined
"""
"""
    Chức năng của generics.CreateAPIView:
        - Nhận và Xử lý POST request từ client: Chỉ chấp nhận phương thức HTTP POST
        - Validate dữ liệu: Chuyển dữ liệu từ request vào serializer để kiểm tra dữ liệu
            - Serializer thực hiện:
                - Validate dữ liệu (kiểm tra định dạng, độ dài, v.v.).
                - Nếu hợp lệ, chuyển dữ liệu thành một instance của model
                - Nếu không hợp lệ, trả về lỗi 400 Bad Request với thông tin chi tiết.
        - Lưu trữ dữ liệu: Lưu đối tượng vào cơ sở dữ liệu nếu dữ liệu hợp lệ.
        - Trả về response: Trả về phản hồi HTTP với dữ liệu của đối tượng vừa tạo.
"""
class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system."""
    # chỉ định view sẽ sử dụng UserSerializer để xử lý dữ liệu đầu vào và đầu ra
    serializer_class = UserSerializer
    
# Kế thừa obtain_auth_token (view có sẵn của DRF) để tận dụng logic tạo token.
class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for a user."""
    # Ghi đè serializer_class để dùng AuthTokenSerializer tùy chỉnh (hỗ trợ email thay vì username).
    serializer_class = AuthTokenSerializer
    # Thêm renderer_classes để đảm bảo giao diện API trong trình duyệt hoạt động
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
    
# Kế thừa RetrieveUpdateAPIView để hỗ trợ GET (truy xuất) và PATCH/PUT (cập nhật).
class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user."""
    # Sử dụng serializer đã tùy chỉnh.
    serializer_class = UserSerializer
    
    # Yêu cầu xác thực bằng token.
    authentication_classes = [authentication.TokenAuthentication]
    
    # Chỉ người dùng đã xác thực mới truy cập được.
    permission_classes = [permissions.IsAuthenticated]

    # Trả về user đã xác thực từ token
    def get_object(self):
        """Retrieve and return the authenticated user."""
        return self.request.user
    