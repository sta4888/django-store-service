import random
import secrets
import string
from django.db import models, ProgrammingError
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.db import connection

from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from django.db import models
import random
import string


def generate_next_internal_id():
    """Безопасная генерация следующего internal_id"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT MAX(internal_id) FROM users_user")
            result = cursor.fetchone()[0]
            return (result or 0) + 1
    except (ProgrammingError, Exception):
        # Если таблица не существует или любая другая ошибка
        return 1


def generate_referral_code():
    """Генерация уникального реферального кода"""
    characters = string.ascii_uppercase + string.digits
    while True:
        code = ''.join(random.choices(characters, k=8))
        if not User.objects.filter(referral_code=code).exists():
            return code


class User(AbstractUser):
    """Кастомная модель пользователя с реферальной системой"""

    # Внутренний ID
    internal_id = models.PositiveIntegerField(
        _('Internal ID'),
        unique=True,
        editable=False,
        null=True,
        blank=True
    )

    # Реферальная система
    referral_code = models.CharField(
        _('Реферальный код'),
        max_length=20,
        unique=True,
        default=generate_referral_code,
        editable=False
    )

    referred_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='referred_users',
        verbose_name=_('Пригласивший пользователь')
    )

    is_external = models.BooleanField(
        _('Внешний пользователь'),
        default=False
    )

    def save(self, *args, **kwargs):
        """Автоматическая генерация internal_id"""
        if not self.internal_id:
            # Находим максимальный internal_id и увеличиваем на 1
            max_id = User.objects.aggregate(models.Max('internal_id'))['internal_id__max'] or 0
            self.internal_id = max_id + 1
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи')


User = get_user_model()


class UserProfile(models.Model):
    """Профиль пользователя с дополнительной информацией для MLM"""

    # Уровни в MLM системе
    LEVEL_CHOICES = [
        ('start', 'Стартовый'),
        ('bronze', 'Бронзовый'),
        ('silver', 'Серебряный'),
        ('gold', 'Золотой'),
        ('platinum', 'Платиновый'),
        ('diamond', 'Алмазный'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name=_('Пользователь')
    )

    # Личная информация
    phone = models.CharField(
        _('Телефон'),
        max_length=20,
        blank=True,
        null=True
    )

    avatar = models.ImageField(
        _('Аватар'),
        upload_to='users/avatars/%Y/%m/%d/',
        blank=True,
        null=True
    )

    birth_date = models.DateField(
        _('Дата рождения'),
        blank=True,
        null=True
    )

    # Адрес
    address = models.TextField(
        _('Адрес доставки'),
        blank=True,
        null=True
    )

    city = models.CharField(
        _('Город'),
        max_length=100,
        blank=True,
        null=True
    )

    postal_code = models.CharField(
        _('Почтовый индекс'),
        max_length=20,
        blank=True,
        null=True
    )

    # MLM Статистика
    level = models.CharField(
        _('Уровень'),
        max_length=20,
        choices=LEVEL_CHOICES,
        default='start'
    )

    personal_volume = models.DecimalField(
        _('Личный объем'),
        max_digits=12,
        decimal_places=2,
        default=0
    )

    group_volume = models.DecimalField(
        _('Групповой объем'),
        max_digits=12,
        decimal_places=2,
        default=0
    )

    earnings = models.DecimalField(
        _('Начисления'),
        max_digits=12,
        decimal_places=2,
        default=0
    )

    available_for_withdrawal = models.DecimalField(
        _('Доступно для вывода'),
        max_digits=12,
        decimal_places=2,
        default=0
    )

    active_partners = models.PositiveIntegerField(
        _('Активных партнеров'),
        default=0
    )

    # Бонусы по категориям
    personal_bonus = models.DecimalField(
        _('Личный бонус'),
        max_digits=12,
        decimal_places=2,
        default=0
    )

    group_bonus = models.DecimalField(
        _('Групповой бонус'),
        max_digits=12,
        decimal_places=2,
        default=0
    )

    leader_bonus = models.DecimalField(
        _('Бонус лидера'),
        max_digits=12,
        decimal_places=2,
        default=0
    )

    # Рост показателей (%)
    personal_volume_growth = models.DecimalField(
        _('Рост личного объема'),
        max_digits=5,
        decimal_places=2,
        default=0
    )

    group_volume_growth = models.DecimalField(
        _('Рост группового объема'),
        max_digits=5,
        decimal_places=2,
        default=0
    )

    earnings_growth = models.DecimalField(
        _('Рост начислений'),
        max_digits=5,
        decimal_places=2,
        default=0
    )

    level_progress = models.PositiveIntegerField(
        _('Прогресс уровня'),
        default=0,
        help_text=_('Процент выполнения до следующего уровня')
    )

    # Настройки
    email_notifications = models.BooleanField(
        _('Email уведомления'),
        default=True
    )

    sms_notifications = models.BooleanField(
        _('SMS уведомления'),
        default=False
    )

    # Статистика покупок
    total_orders = models.PositiveIntegerField(
        _('Всего заказов'),
        default=0
    )

    total_spent = models.DecimalField(
        _('Всего потрачено'),
        max_digits=12,
        decimal_places=2,
        default=0
    )

    created_at = models.DateTimeField(
        _('Создан'),
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        _('Обновлен'),
        auto_now=True
    )

    class Meta:
        verbose_name = _('Профиль пользователя')
        verbose_name_plural = _('Профили пользователей')
        ordering = ['-created_at']

    def __str__(self):
        return f'Профиль {self.user.username}'

    @property
    def full_name(self):
        """Полное имя пользователя"""
        return f'{self.user.first_name} {self.user.last_name}'.strip() or self.user.username

    @property
    def referral_count(self):
        """Количество приглашенных пользователей"""
        return User.objects.filter(referred_by=self.user).count()

    @property
    def monthly_earnings(self):
        """Начисления за текущий месяц"""
        # Здесь можно добавить логику расчета
        return self.earnings * 0.3  # Пример: 30% от общих начислений

    @property
    def status(self):
        """Статус для отображения в интерфейсе"""
        return self.get_level_display()

    def get_level_display_with_color(self):
        """Отображение уровня с цветом"""
        colors = {
            'start': 'secondary',
            'bronze': 'warning',
            'silver': 'light',
            'gold': 'warning',
            'platinum': 'info',
            'diamond': 'primary',
        }
        return f'<span class="badge bg-{colors.get(self.level, "secondary")}">{self.get_level_display()}</span>'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Создание профиля при создании пользователя"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Сохранение профиля при сохранении пользователя"""
    try:
        instance.profile.save()
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(user=instance)
