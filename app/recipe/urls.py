"""URL mappings for the recipe app."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from recipe import views

# Sử dụng DefaultRouter để tự động tạo URL cho RecipeViewSet.
router = DefaultRouter()
# Đăng ký RecipeViewSet với prefix recipes, tạo endpoint /recipes/ và /recipes/<id>/.
router.register('recipes', views.RecipeViewSet)
# Đặt namespace cho URL (recipe:recipe-list)
app_name = 'recipe'
urlpatterns = [
    path('', include(router.urls)),
]