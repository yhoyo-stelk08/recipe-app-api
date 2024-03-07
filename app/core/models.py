"""
Custom user model
"""

from django.db import models
from django.contrib.auth.models import AbstractBaseUser,PermissionsMixin,BaseUserManager


class User(AbstractBaseUser, PermissionsMixin):
    """Make custom user model extends from AbstractBaseUser"""

    # declare fields
    email = models.EmailField(unique=True,max_length=100)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'