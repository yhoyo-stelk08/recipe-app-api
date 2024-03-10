"""
Serializers of Recipe API
"""
from rest_framework import serializers

from core.models import Recipe, Tag


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for Recipe models."""

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'time_minutes', 'price', 'link']
        read_only_fields = ['id']


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for recipe details"""

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['desc']


class TagSerializer(serializers.ModelSerializer):
    """Serializer fo Tag"""
    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_field = ['id']
