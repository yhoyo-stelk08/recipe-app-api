"""
Custom user model
"""
import uuid
import os

from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, \
    PermissionsMixin, BaseUserManager


def recipe_image_file_path(instance, filename):
    """Generate file path for a new recipe image."""
    file_extension = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{file_extension}'
    # print(os.path.join('uploads', 'recipe', filename))
    return os.path.join('uploads', 'recipe', filename)


class UserManager(BaseUserManager):
    """Manager for class User"""

    def create_user(self, email, password=None, **extra_field):
        """create,save and return user"""
        if not email:
            raise ValueError('User must have email address.')
        user = self.model(email=self.normalize_email(email), **extra_field)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """create,save and return superuser"""
        user = self.create_user(email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Make custom user model extends from AbstractBaseUser"""

    # declare fields
    email = models.EmailField(unique=True, max_length=100)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'


class Recipe(models.Model):
    """Model for recipe"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=255)
    desc = models.TextField(blank=True)
    time_minutes = models.IntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    link = models.CharField(max_length=255, blank=True)
    tags = models.ManyToManyField('Tag')
    ingredients = models.ManyToManyField('Ingredient')
    image = models.ImageField(null=True, upload_to=recipe_image_file_path)

    def __str__(self):
        return self.title


class Tag(models.Model):
    """Model for Tag"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Model for ingredients."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
