"""
Custom user model
"""

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, \
    PermissionsMixin, BaseUserManager


class UserManager(BaseUserManager):
    """Manager for class User"""

    def create_user(self, email, password=None, **other_field):
        """create,save and return user"""
        if not email:
            raise ValueError('User must have email address.')
        user = self.model(email=self.normalize_email(email), **other_field)
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
