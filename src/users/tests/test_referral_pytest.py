import pytest


@pytest.mark.django_db
def test_referral_code_generation():
    """Тест генерации реферального кода"""
    from django.contrib.auth import get_user_model
    User = get_user_model()

    user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='password123'
    )

    assert user.referral_code is not None
    assert len(user.referral_code) == 8
    assert user.referral_code.isalnum()


@pytest.mark.django_db
def test_referral_code_uniqueness():
    """Тест уникальности реферальных кодов"""
    from django.contrib.auth import get_user_model
    User = get_user_model()

    user1 = User.objects.create_user(
        username='user1',
        email='user1@example.com',
        password='pass123'
    )

    user2 = User.objects.create_user(
        username='user2',
        email='user2@example.com',
        password='pass123'
    )

    assert user1.referral_code != user2.referral_code

# И так для всех тестов - импортируй get_user_model внутри функции