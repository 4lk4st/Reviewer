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
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        create_roles_and_permissions()
        return user

    def create_superuser(self, username, email=None, password=None,
                         **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        create_roles_and_permissions()
        admin_group = Group.objects.get(name='admin')
        extra_fields['role'] = admin_group
        return self.create_user(username, email, password, **extra_fields)


class User(AbstractUser):
    USER_ROLE_USER = 'user'
    USER_ROLE_MODERATOR = 'moderator'
    USER_ROLE_ADMIN = 'admin'
    ROLE_CHOICES = [
        ('user', 'User'),
        ('moderator', 'Moderator'),
        ('admin', 'Admin'),
    ]
    username = models.CharField(
        unique=True,
        max_length=150,
        verbose_name='Имя пользователя',
        validators=[
            validators.RegexValidator(r'^[\w.@+-]+$',
                                      _('Enter a valid username. '
                                        'This value may contain '
                                        'only letters, numbers '
                                        'and @/./+/-/_ characters.'),
                                      'invalid'),
        ],)
    email = models.EmailField(
        unique=True, max_length=254,
        verbose_name='Почта')
    bio = models.TextField(verbose_name='Биография', blank=True)
    role = models.CharField(
        verbose_name='Роль', max_length=30, choices=ROLE_CHOICES,
        default=USER_ROLE_USER)
    confirmation_code = models.CharField(max_length=30, blank=True)
    objects = UserManager()

    class Meta:
        ordering = ['-username']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
