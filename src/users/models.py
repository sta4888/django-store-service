import secrets
import string
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.db import connection


def generate_next_internal_id():
    """Генерация следующего internal_id"""
    with connection.cursor() as cursor:
        cursor.execute("SELECT MAX(internal_id) FROM users_user")
        result = cursor.fetchone()
        max_id = result[0]

    if not max_id:
        return '000001'

    try:
        next_id = int(max_id) + 1
    except ValueError:
        next_id = 1

    return f"{next_id:06d}"


def generate_referral_code(length=8):
    """Генерация реферального кода"""
    alphabet = string.ascii_letters + string.digits
    while True:
        code = ''.join(secrets.choice(alphabet) for _ in range(length))
        # Проверяем уникальность
        from .models import User
        if not User.objects.filter(referral_code=code).exists():
            return code


class User(AbstractUser):
    """Кастомная модель пользователя"""

    # 1. Внутренний ID
    internal_id = models.CharField(
        _('Internal ID'),
        max_length=10,
        unique=True,
        default=generate_next_internal_id,
        editable=False,
        db_index=True
    )

    # 2. Реферальный код
    referral_code = models.CharField(
        _('Referral Code'),
        max_length=20,
        unique=True,
        blank=True,
        null=True,
        db_index=True
    )

    # 3. Кто пригласил
    referrer = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='referred_users',
        verbose_name=_('Referrer')
    )

    # 4. Флаг внешнего пользователя
    is_external = models.BooleanField(
        _('External User'),
        default=False,
        help_text=_('User created from external service')
    )

    # 5. Флаг партнёра
    is_partner = models.BooleanField(
        _('Is Partner'),
        default=False
    )

    # 6. Дата создания (дублируем date_joined для ясности)
    created_at = models.DateTimeField(
        _('Created at'),
        auto_now_add=True
    )

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['internal_id']

    def __str__(self):
        return f"{self.internal_id} - {self.username}"

    def save(self, *args, **kwargs):
        """Переопределяем save для генерации полей"""
        # Генерируем internal_id если его нет
        if not self.internal_id:
            self.internal_id = generate_next_internal_id()

        # Генерируем referral_code если его нет
        if not self.referral_code:
            self.referral_code = generate_referral_code()

        super().save(*args, **kwargs)

    def get_referral_link(self):
        """Генерирует реферальную ссылку"""
        from django.conf import settings
        base_url = settings.SITE_URL.rstrip('/')
        return f"{base_url}/ref/{self.referral_code}/"

    def get_referral_stats(self):
        """Получает статистику по рефералам"""
        return {
            'total_referrals': self.referred_users.count(),
            'direct_referrals': self.referred_users.filter(referrer=self).count(),
        }