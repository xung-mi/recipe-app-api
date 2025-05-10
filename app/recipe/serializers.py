"""Serializer for recipe APIs."""
from rest_framework import serializers
from core.models import Recipe

# Dùng để serialize/deserialize dữ liệu recipe cho API.
class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipes."""
    class Meta:
        model = Recipe
        fields = ['id', 'title', 'time_minutes', 'price', 'link']
        read_only_fields = ['id']

# Kế thừa RecipeSerializer để tái sử dụng cấu hình (model, fields, read_only_fields).
class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for recipe detail view."""
    
    # Dùng Meta kế thừa từ RecipeSerializer.Meta và thêm description vào fields.
    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']