from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
import uuid
from django.utils import timezone


class CustomUser(AbstractUser):
    # Основные поля
    user_id = models.CharField(
        max_length=8,
        unique=True,
        editable=False,
        verbose_name='ID пользователя'
    )
    phone = models.CharField(
        max_length=20,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', 'Введите корректный номер телефона')],
        verbose_name='Телефон'
    )
    country = models.CharField(
        max_length=100,
        verbose_name='Страна'
    )

    # Новые поля для регистрации
    middle_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Отчество'
    )
    passport_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Номер паспорта'
    )
    is_terms_accepted = models.BooleanField(
        default=False,
        verbose_name='Согласие на обработку данных'
    )
    is_email_verified = models.BooleanField(
        default=False,
        verbose_name='Email подтвержден'
    )
    email_verification_code = models.CharField(
        max_length=6,
        blank=True,
        null=True,
        verbose_name='Код подтверждения email'
    )
    email_verification_sent_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Время отправки кода подтверждения'
    )

    # Реферальные поля
    referral_code = models.CharField(
        max_length=32,
        unique=True,
        editable=False,
        verbose_name='Реферальный код'
    )
    referrer = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='referrals',
        verbose_name='Пригласивший пользователь'
    )
    referral_link = models.CharField(
        max_length=255,
        unique=True,
        editable=False,
        verbose_name='Реферальная ссылка'
    )

    # Статистические поля
    personal_volume = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Личный объем'
    )
    group_volume = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Групповой объем'
    )
    earnings = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Начисления'
    )
    available_for_withdrawal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Доступно для вывода'
    )
    partner_level = models.CharField(
        max_length=50,
        default='Начинающий',
        verbose_name='Уровень партнера'
    )
    registration_date = models.DateField(
        auto_now_add=True,
        verbose_name='Дата регистрации'
    )
    is_partner = models.BooleanField(
        default=True,
        verbose_name='Партнер'
    )

    # Статистика по рефералам
    total_referrals = models.PositiveIntegerField(
        default=0,
        verbose_name='Всего приглашенных'
    )
    active_referrals = models.PositiveIntegerField(
        default=0,
        verbose_name='Активных рефералов'
    )

    def save(self, *args, **kwargs):
        if not self.user_id:
            # Генерация ID в формате 00000001
            last_user = CustomUser.objects.order_by('id').last()
            if last_user:
                last_id = int(last_user.user_id)
                new_id = str(last_id + 1).zfill(8)
            else:
                new_id = '00000001'
            self.user_id = new_id

        if not self.referral_code:
            # Генерация уникального реферального кода
            self.referral_code = uuid.uuid4().hex[:16].upper()

        if not self.referral_link:
            # Генерация реферальной ссылки
            self.referral_link = f"ref-{self.referral_code}"

        if not self.username:
            self.username = self.user_id

        super().save(*args, **kwargs)

    def get_full_referral_url(self, request=None):
        """Получение полной реферальной ссылки"""
        if request:
            domain = request.get_host()
            return f"http://{domain}/register/{self.referral_link}/"
        return f"/register/{self.referral_link}/"

    def generate_email_verification_code(self):
        """Генерация кода подтверждения email"""
        import random
        self.email_verification_code = str(random.randint(100000, 999999))
        self.email_verification_sent_at = timezone.now()
        self.save()
        return self.email_verification_code

    def is_verification_code_expired(self):
        """Проверка истечения срока действия кода"""
        if not self.email_verification_sent_at:
            return True
        expired_time = self.email_verification_sent_at + timezone.timedelta(minutes=15)
        return timezone.now() > expired_time

    def __str__(self):
        return f"{self.user_id} - {self.get_full_name() or self.username}"

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'