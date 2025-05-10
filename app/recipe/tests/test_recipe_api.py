"""Tests for recipe APIs."""

from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Recipe
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

recipes_url = reverse('recipe:recipe-list')

'''
    Recipe
'''

# Hàm Helper để tạo recipe test, Giảm code lặp khi tạo recipe trong test, cho phép tùy chỉnh khi cần.
def create_recipe(user, **params):
    """Create and return a sample recipe."""
    defaults = {
        'title': 'Sample recipe title',
        'time_minutes': 22,
        'price': Decimal('5.25'),
        'description': 'Sample description',
        'link': 'http://example.com/recipe.pdf'
    }
    defaults.update(params)
    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe

"""
    Recipe Detail
"""

# Hàm helper để tạo URL chi tiết recipe
def detail_url(recipe_id):
    """Create and return a recipe detail URL."""
    return reverse('recipe:recipe-detail', args=[recipe_id])

# Hàm helper Giảm lặp code khi tạo user test
def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


# Không xác thực
class PublicRecipeApiTests(TestCase):
    """Test unauthenticated API requests."""
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API."""
        res = self.client.get(recipes_url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        
# Chuẩn bị cho các test yêu cầu xác thực (như liệt kê recipes của user).
class PrivateRecipeApiTests(TestCase):
    """Test authenticated API requests."""
    def setUp(self):
        self.client = APIClient()
        # self.user = get_user_model().objects.create_user(
        #     'user@example.com',
        #     'testpass123'
        # )
        self.user = create_user(email='user@example.com', password='test123')
        
        # Giả lập xác thực để test các request đã xác thực.
        self.client.force_authenticate(self.user)
        
    # Truy xuất danh sách Recipes
    def test_retrieve_recipes(self):
        """Test retrieving a list of recipes."""
        create_recipe(user=self.user)
        create_recipe(user=self.user)
        res = self.client.get(recipes_url)
        # sắp xếp theo id giảm dần
        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        
    # Chỉ trả về Recipes của User đã xác thực
    def test_recipe_list_limited_to_user(self):
        """Test list of recipes is limited to authenticated user."""
        other_user = create_user(email='other@example.com', password='password123')
        
        create_recipe(user=other_user)
        create_recipe(user=self.user)
        res = self.client.get(recipes_url)
        recipes = Recipe.objects.filter(user=self.user)
        # Lấy recipes chỉ từ user đã xác thực
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        
    
    def test_get_recipe_detail(self):
        """Test get recipe detail."""
        recipe = create_recipe(user=self.user)
        url = detail_url(recipe.id)
        res = self.client.get(url)
        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)
        
    def test_create_recipe(self):
        """Test creating a recipe."""
        payload = {
            'title': 'Sample recipe',
            'time_minutes': 30,
            'price': Decimal('5.99')
        }
        res = self.client.post(recipes_url, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        for k, v in payload.items():
            # getattr Lấy giá trị thuộc tính của recipe (như recipe.title) dựa trên tên thuộc tính động (k).
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)
        
        
    def test_partial_update(self):
        """Test partial update of a recipe."""
        original_link = 'https://example.com/recipe.pdf'
        recipe = create_recipe(
            user=self.user,
            title='Sample recipe title',
            link=original_link
        )
        payload = {'title': 'New recipe title'}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # lấy dữ liệu mới từ database vì Django không tự động cập nhật object sau khi thay đổi qua API
        # refresh_from_db() tải lại dữ liệu từ database để phản ánh thay đổi từ PATCH
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.link, original_link)
        self.assertEqual(recipe.user, self.user)
        
    # Test Full Update (PUT
    def test_full_update(self):
        """Test full update of recipe."""
        recipe = create_recipe(
            user=self.user,
            title='Sample recipe title',
            link='https://example.com/recipe.pdf',
            description='Sample recipe description'
        )
        payload = {
            'title': 'New recipe title',
            'link': 'https://example.com/new-recipe.pdf',
            'description': 'New recipe description',
            'time_minutes': 10,
            'price': Decimal('2.50')
        }
        url = detail_url(recipe.id)
        res = self.client.put(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        # User không thay đổi, vẫn là user đã xác thực.
        self.assertEqual(recipe.user, self.user)
        
    # Test Ngăn Cập nhật User
    def test_update_user_returns_error(self):
        """Test changing the recipe user results in an error."""
        new_user = create_user(email='user2@example.com', password='test123')
        recipe = create_recipe(user=self.user)
        payload = {'user': new_user.id}
        url = detail_url(recipe.id)
        self.client.patch(url, payload)
        recipe.refresh_from_db()
        self.assertEqual(recipe.user, self.user)
        
    # Test Xóa Recipe
    def test_delete_recipe(self):
        """Test deleting a recipe successful."""
        recipe = create_recipe(user=self.user)
        url = detail_url(recipe.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())
        
    # Test Xóa Recipe của User Khác => Ngăn xóa recipe của user khác (bảo mật).
    def test_delete_other_users_recipe_error(self):
        """Test trying to delete another user's recipe gives error."""
        new_user = create_user(email='user2@example.com', password='test123')
        recipe = create_recipe(user=new_user)
        url = detail_url(recipe.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())
        
    
    
        
