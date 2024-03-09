"""
Serializers of Recipe API
"""
from rest_framework import serializers

from core.models import Recipe


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for Recipe models."""

    class Meta:
        model = Recipe
        fields = ['id','title','time_minutes','price','link', 'desc']
        read_only_fields = ['id']
