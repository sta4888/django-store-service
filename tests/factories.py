import factory
import secrets
import string
from django.contrib.auth import get_user_model

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    """Фабрика для создания пользователей"""

    class Meta:
        model = User
        django_get_or_create = ('username',)

    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    password = factory.PostGenerationMethodCall('set_password', 'password123')

    # Дополнительные поля
    is_external = False
    is_partner = False

    @factory.lazy_attribute
    def referral_code(self):
        """Генерация уникального реферального кода"""
        alphabet = string.ascii_letters + string.digits
        while True:
            code = ''.join(secrets.choice(alphabet) for _ in range(8))
            # Проверяем уникальность вручную
            if not User.objects.filter(referral_code=code).exists():
                return code

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Переопределяем для обработки referrer"""
        referrer = kwargs.pop('referrer', None)
        user = super()._create(model_class, *args, **kwargs)

        if referrer:
            user.referrer = referrer
            user.save()

        return user


# Специальные фабрики
class ExternalUserFactory(UserFactory):
    """Фабрика для внешних пользователей"""
    is_external = True
    username = None  # Внешние пользователи могут не иметь username


class PartnerUserFactory(UserFactory):
    """Фабрика для партнёров"""
    is_partner = True


class AdminUserFactory(UserFactory):
    """Фабрика для администраторов"""
    is_staff = True
    is_superuser = True