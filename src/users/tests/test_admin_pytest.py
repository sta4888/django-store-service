import pytest
from django.contrib.admin.sites import AdminSite
from django.test import RequestFactory
from users.admin import CustomUserAdmin
from users.models import User


@pytest.mark.django_db
class TestUserAdmin:
    """Тесты админки пользователей"""

    @pytest.fixture
    def admin_site(self):
        return AdminSite()

    @pytest.fixture
    def user_admin(self, admin_site):
        return CustomUserAdmin(User, admin_site)

    @pytest.fixture
    def request_factory(self):
        return RequestFactory()

    def test_list_display(self, user_admin):
        """Тест полей в списке"""
        expected_fields = [
            'internal_id', 'username', 'email',
            'referral_code', 'is_external', 'is_partner', 'is_staff'
        ]
        assert list(user_admin.list_display) == expected_fields

    def test_search_fields(self, user_admin):
        """Тест полей поиска"""
        expected_fields = ['internal_id', 'username', 'email', 'referral_code']
        assert list(user_admin.search_fields) == expected_fields

    def test_list_filter(self, user_admin):
        """Тест фильтров"""
        expected_filters = [
            'is_staff', 'is_superuser', 'is_active',
            'is_external', 'is_partner'
        ]
        assert list(user_admin.list_filter) == expected_filters

    def test_readonly_fields(self, user_admin):
        """Тест read-only полей"""
        expected_fields = ['internal_id', 'referral_code', 'created_at']
        assert list(user_admin.readonly_fields) == expected_fields


@pytest.mark.django_db
def test_user_creation_via_admin(client, admin_user):
    """Тест создания пользователя через админку"""
    client.force_login(admin_user)

    response = client.get('/admin/users/user/add/')
    assert response.status_code == 200

    # Проверяем что форма содержит нужные поля
    content = response.content.decode()
    assert 'username' in content
    assert 'email' in content
    assert 'is_external' in content
    assert 'is_partner' in content