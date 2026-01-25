import os
import sys
import pytest
import django
from django.conf import settings

# Добавляем пути
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'src'))


def pytest_configure():
    """Настройка pytest при запуске"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

    if not settings.configured:
        settings.configure(
            DEBUG=True,
            DATABASES={
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': ':memory:',
                }
            },
            INSTALLED_APPS=[
                'django.contrib.admin',
                'django.contrib.auth',
                'django.contrib.contenttypes',
                'django.contrib.sessions',
                'django.contrib.messages',
                'django.contrib.staticfiles',
                'users',
            ],
            AUTH_USER_MODEL='users.User',
            SECRET_KEY='test-secret-key',
            USE_TZ=True,
            TIME_ZONE='UTC',
            LANGUAGE_CODE='en-us',
            ROOT_URLCONF='src.core.urls',
            MIDDLEWARE=[
                'django.middleware.security.SecurityMiddleware',
                'django.contrib.sessions.middleware.SessionMiddleware',
                'django.middleware.common.CommonMiddleware',
                'django.middleware.csrf.CsrfViewMiddleware',
                'django.contrib.auth.middleware.AuthenticationMiddleware',
                'django.contrib.messages.middleware.MessageMiddleware',
                'django.middleware.clickjacking.XFrameOptionsMiddleware',
            ],
        )

    django.setup()


# Фикстуры
@pytest.fixture
def User():
    """Фикстура для получения модели пользователя"""
    from django.contrib.auth import get_user_model
    return get_user_model()


@pytest.fixture
def user(db, User):
    """Фикстура для создания тестового пользователя"""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='password123'
    )


@pytest.fixture
def admin_user(db, User):
    """Фикстура для создания администратора"""
    return User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='admin123'
    )


@pytest.fixture
def external_user(db, User):
    """Фикстура для внешнего пользователя"""
    return User.objects.create_user(
        username='external',
        email='external@example.com',
        password='password123',
        is_external=True
    )


@pytest.fixture
def partner_user(db, User):
    """Фикстура для партнёра"""
    return User.objects.create_user(
        username='partner',
        email='partner@example.com',
        password='password123',
        is_partner=True
    )


@pytest.fixture
def user_with_referrer(db, User):
    """Фикстура для пользователя с реферером"""
    referrer = User.objects.create_user(
        username='referrer',
        email='referrer@example.com',
        password='password123'
    )

    referred = User.objects.create_user(
        username='referred',
        email='referred@example.com',
        password='password123',
        referrer=referrer
    )

    return {
        'referrer': referrer,
        'referred': referred
    }