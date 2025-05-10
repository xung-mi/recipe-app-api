"""Views for the recipe APIs."""
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from core.models import Recipe
from recipe import serializers

# Kế thừa ModelViewSet để hỗ trợ CRUD (list, create, retrieve, update, destroy).
class RecipeViewSet(viewsets.ModelViewSet):
    """View for manage recipe APIs."""
    serializer_class = serializers.RecipeDetailSerializer
    queryset = Recipe.objects.all()
    
    #Yêu cầu xác thực token và user phải đăng nhập.
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    # Ghi đè get_queryset: Lọc recipes theo user đã xác thực và sắp xếp theo id giảm dần
    def get_queryset(self):
        """Retrieve recipes for authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-id')
    
    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == 'list':
            return serializers.RecipeSerializer # RecipeSerializer cho danh sách để tối ưu (ít dữ liệu hơn).
        return self.serializer_class            # RecipeDetailSerializer cho chi tiết để cung cấp đầy đủ thông tin.
    
    # Ghi đè phương thức của ModelViewSet để tùy chỉnh logic tạo object.
    # Được gọi tự động khi tạo recipe qua POST request (/recipes/).
    # Nhận serializer đã được validate (dữ liệu từ payload đã hợp lệ).
    def perform_create(self, serializer):
        """Create a new recipe."""
        # Lưu recipe với user là user đã xác thực (self.request.user), đảm bảo trường user được gán đúng.
        serializer.save(user=self.request.user)