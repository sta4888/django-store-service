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


class News(models.Model):
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    content = models.TextField(verbose_name='Содержание')
    date = models.DateField(verbose_name='Дата публикации')
    is_published = models.BooleanField(default=True, verbose_name='Опубликовано')

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'
        ordering = ['-date']