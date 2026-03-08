from django.db import models
from django.conf import settings


class Purchase(models.Model):
    STATUS_CHOICES = [
        ('pending', 'В обработке'),
        ('shipped', 'Отправлен'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменен'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='purchases')
    order_number = models.CharField(max_length=50, verbose_name='Номер заказа')
    product_name = models.CharField(max_length=200, verbose_name='Название товара')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Сумма')
    date = models.DateField(verbose_name='Дата покупки')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Статус')
    bonus = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Бонус')

    class Meta:
        verbose_name = 'Покупка'
        verbose_name_plural = 'Покупки'
        ordering = ['-date']


class MonthlyReport(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='monthly_reports', verbose_name='Пользователь')
    year = models.PositiveSmallIntegerField(verbose_name='Год')
    month = models.PositiveSmallIntegerField(verbose_name='Месяц')

    # Объёмы (lo, go, side_volume из FastAPI)
    personal_volume = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Личный объём (LO)')
    group_volume = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Групповой объём (GO)')
    side_volume = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Боковой объём')

    # Баллы и вероны (points, veron из FastAPI)
    points = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Баллы')
    veron = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Вероны')

    # Бонусы (из FastAPI)
    personal_bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Личный бонус')
    structure_bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Структурный бонус')
    mentor_bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Менторский бонус')
    extra_bonus = models.CharField(max_length=100, blank=True, default='', verbose_name='Доп. бонус')
    bonus_total = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Суммарный бонус')

    # Доход с разбивкой (из FastAPI)
    personal_money = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Личный доход')
    group_money = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Групповой доход')
    leader_money = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Лидерский доход')
    side_vol_money = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Доход с бокового объёма')
    total_money = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Итого доход')
    total_income = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Общий доход')

    # Рефералы
    new_referrals = models.PositiveIntegerField(default=0, verbose_name='Новые рефералы')
    active_referrals_count = models.PositiveIntegerField(default=0, verbose_name='Активные рефералы')

    # Покупки (из Django БД)
    purchases_count = models.PositiveIntegerField(default=0, verbose_name='Количество заказов')
    purchases_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Сумма заказов')

    # Статус
    partner_level = models.CharField(max_length=100, blank=True, verbose_name='Уровень партнёра')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Месячный отчёт'
        verbose_name_plural = 'Месячные отчёты'
        ordering = ['-year', '-month']
        unique_together = ('user', 'year', 'month')


class News(models.Model):
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    content = models.TextField(verbose_name='Содержание')
    date = models.DateField(verbose_name='Дата публикации')
    is_published = models.BooleanField(default=True, verbose_name='Опубликовано')

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'
        ordering = ['-date']