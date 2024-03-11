"""
Views for Recipe API
"""
from rest_framework import (
    viewsets,
    mixins,
    status,
)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe, Tag, Ingredient
from recipe import serializers


class BaseClassRecipeAttrViewset(
        mixins.DestroyModelMixin,
        mixins.UpdateModelMixin,
        mixins.ListModelMixin,
        viewsets.GenericViewSet):
    """Base class for recipe attributes."""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by('-name')


class RecipeViewSet(viewsets.ModelViewSet):
    """View for manage Recipes APIs."""
    serializer_class = serializers.RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """retrieve recipes for current authenticated user"""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """return the serializer class for request."""
        if self.action == 'list':
            self.serializer_class = serializers.RecipeSerializer
        elif self.action == 'upload_image':
            self.serializer_class = serializers.RecipeImageSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new recipe."""
        serializer.save(user=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image to recipe."""
        recipe = self.get_object()
        # print(recipe)
        serializer = self.get_serializer(recipe, data=request.data)
        # print(serializer)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class IngredientViewSet(BaseClassRecipeAttrViewset):
    """View for manage Ingredient API."""
    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()


class TagViewSet(BaseClassRecipeAttrViewset):
    """View for manage Tags API."""
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()
