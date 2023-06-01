from django.apps import apps
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


def create_roles_and_permissions():
    # Создаем группы пользователей
    user_group, _ = Group.objects.get_or_create(name='user')
    moderator_group, _ = Group.objects.get_or_create(name='moderator')
    admin_group, _ = Group.objects.get_or_create(name='admin')

    # Получаем все модели в проекте
    all_models = apps.get_models()

    # Перебираем все модели и добавляем права доступа для них
    for model in all_models:
        content_type = ContentType.objects.get_for_model(model)

        # Разрешение на удаление
        delete_permission, _ = Permission.objects.get_or_create(
            content_type=content_type,
            codename='delete_%s' % model._meta.model_name,
            defaults={'name': 'Can delete %s' % model._meta.verbose_name}
        )

        # Разрешение на изменение
        change_permission, _ = Permission.objects.get_or_create(
            content_type=content_type,
            codename='change_%s' % model._meta.model_name,
            defaults={'name': 'Can change %s' % model._meta.verbose_name}
        )

        # Разрешение на добавление
        add_permission, _ = Permission.objects.get_or_create(
            content_type=content_type,
            codename='add_%s' % model._meta.model_name,
            defaults={'name': 'Can add %s' % model._meta.verbose_name}
        )

        # Добавляем разрешения к соответствующей группе пользователей
        if model._meta.model_name == 'user':
            # Разрешения для модели User
            user_group.permissions.add(change_permission)
        elif model._meta.model_name == 'moderator':
            # Разрешения для модели Moderator
            moderator_group.permissions.add(change_permission)
            moderator_group.permissions.add(delete_permission)
        elif model._meta.model_name == 'admin':
            # Разрешения для модели Admin
            admin_group.permissions.add(change_permission)
            admin_group.permissions.add(delete_permission)
            admin_group.permissions.add(add_permission)

    return user_group, moderator_group, admin_group
