from django.contrib.auth.models import AbstractUser, BaseUserManager, Group
from django.db import models
from django.core import validators
from django.utils.translation import gettext_lazy as _

from .permissions import create_roles_and_permissions


def default_related_model():
    group = Group.objects.get(name='user')
    return group


class UserManager(BaseUserManager):
    def create_user(self, username, email=None, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username field must be set')
        if username == 'me':
            raise ValueError('нельзя использовать - me - для username')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        create_roles_and_permissions()
        return user

    def create_superuser(self, username, email=None, password=None,
                         **extra_fields):
        if username == 'me':
            raise ValueError('нельзя использовать - me - для username')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        create_roles_and_permissions()
        admin_group = Group.objects.get(name='admin')
        extra_fields['role'] = admin_group
        return self.create_user(username, email, password, **extra_fields)


class User(AbstractUser):
    username = models.CharField(
        unique=True,
        max_length=150,
        validators=[
            validators.RegexValidator(r'^[\w.@+-]+$',
                                      _('Enter a valid username. '
                                        'This value may contain '
                                        'only letters, numbers '
                                        'and @/./+/-/_ characters.'), 'invalid'),
        ],)
    email = models.EmailField(unique=True, max_length=254)
    bio = models.TextField('Биография', blank=True)
    ROLE_CHOICES = [
        ('user', 'User'),
        ('moderator', 'Moderator'),
        ('admin', 'Admin'),
    ]
    role = models.CharField('Роль', max_length=30, choices=ROLE_CHOICES,
                            default='user')
    confirmation_code = models.CharField(max_length=30, blank=True)
    objects = UserManager()

    class Meta:
        ordering = ['-username']
