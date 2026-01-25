from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.core.exceptions import ValidationError


class Category(models.Model):
    """Модель категорий товаров"""

    name = models.CharField(
        _('Name'),
        max_length=200,
        db_index=True
    )

    slug = models.SlugField(
        _('Slug'),
        max_length=200,
        unique=True,
        db_index=True,
        blank=True
    )

    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name=_('Parent category')
    )

    description = models.TextField(
        _('Description'),
        blank=True
    )

    is_active = models.BooleanField(
        _('Is active'),
        default=True
    )

    is_root = models.BooleanField(
        _('Is root category'),
        default=False,
        help_text=_('Root category for breadcrumbs')
    )

    created_at = models.DateTimeField(
        _('Created at'),
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        _('Updated at'),
        auto_now=True
    )

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        ordering = ['name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Переопределяем save для генерации slug"""
        # Генерируем slug если он пустой
        if not self.slug or self.slug.strip() == '':
            base_slug = slugify(self.name)
            slug = base_slug

            # Проверяем уникальность slug
            counter = 1
            while Category.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    # Удаляем метод get_level или заменяем на свой
    def get_level(self):
        """Получение уровня вложенности (упрощённо)"""
        level = 0
        parent = self.parent
        while parent:
            level += 1
            parent = parent.parent
        return level

    def get_absolute_url(self):
        return reverse('catalog:category_detail', args=[self.slug])

    def get_breadcrumbs(self):
        """Получение хлебных крошек для категории"""
        from django.urls import reverse

        breadcrumbs = []
        current = self

        # Поднимаемся вверх по иерархии
        while current:
            breadcrumbs.insert(0, {
                'name': current.name,
                'url': current.get_absolute_url()
            })
            current = current.parent

        # Добавляем главную страницу каталога если нужно
        if not breadcrumbs or breadcrumbs[0]['name'] != 'Каталог':
            breadcrumbs.insert(0, {
                'name': 'Каталог',
                'url': reverse('catalog:index')
            })

        return breadcrumbs


class ActiveProductManager(models.Manager):
    """Менеджер для активных товаров"""

    def get_queryset(self):
        return super().get_queryset().filter(
            is_active=True,
            category__is_active=True
        )


class Attribute(models.Model):
    """Модель атрибута товара"""

    FILTER_TYPES = [
        ('multi', 'Множественный выбор'),
        ('range', 'Диапазон'),
        ('boolean', 'Да/Нет'),
    ]

    name = models.CharField(
        _('Name'),
        max_length=100
    )

    code = models.SlugField(
        _('Code'),
        max_length=100,
        unique=True
    )

    filter_type = models.CharField(
        _('Filter type'),
        max_length=10,
        choices=FILTER_TYPES,
        default='multi'
    )

    unit = models.CharField(
        _('Unit'),
        max_length=20,
        blank=True
    )

    order = models.PositiveIntegerField(
        _('Order'),
        default=0
    )

    class Meta:
        verbose_name = _('Attribute')
        verbose_name_plural = _('Attributes')
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class AttributeValue(models.Model):
    """Модель значения атрибута"""

    attribute = models.ForeignKey(
        Attribute,
        on_delete=models.CASCADE,
        related_name='values',
        verbose_name=_('Attribute')
    )

    value = models.CharField(
        _('Value'),
        max_length=100
    )

    code = models.SlugField(
        _('Code'),
        max_length=100
    )

    order = models.PositiveIntegerField(
        _('Order'),
        default=0
    )

    class Meta:
        verbose_name = _('Attribute value')
        verbose_name_plural = _('Attribute values')
        ordering = ['attribute', 'order', 'value']
        unique_together = ['attribute', 'code']

    def __str__(self):
        return f"{self.attribute.name}: {self.value}"


class Product(models.Model):
    """Модель товара"""

    name = models.CharField(
        _('Name'),
        max_length=200,
        db_index=True
    )

    slug = models.SlugField(
        _('Slug'),
        max_length=200,
        unique=True,
        db_index=True,
        blank=True
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name=_('Category')
    )

    sku = models.CharField(
        _('SKU'),
        max_length=50,
        unique=True,
        blank=True,
        null=True
    )

    price = models.DecimalField(
        _('Price'),
        max_digits=10,
        decimal_places=2
    )

    old_price = models.DecimalField(
        _('Old price'),
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )

    description = models.TextField(
        _('Description'),
        blank=True
    )

    short_description = models.TextField(
        _('Short description'),
        max_length=500,
        blank=True
    )

    attributes = models.ManyToManyField(
        AttributeValue,
        related_name='products',
        verbose_name=_('Attributes'),
        blank=True
    )

    in_stock = models.BooleanField(
        _('In stock'),
        default=True
    )

    quantity = models.PositiveIntegerField(
        _('Quantity'),
        default=0
    )

    is_active = models.BooleanField(
        _('Is active'),
        default=True
    )

    created_at = models.DateTimeField(
        _('Created at'),
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        _('Updated at'),
        auto_now=True
    )

    # Менеджеры
    objects = models.Manager()
    active_products = ActiveProductManager()

    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _('Products')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['price']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Переопределяем save для генерации slug и проверки количества"""

        # Генерируем slug если он пустой
        if not self.slug or self.slug.strip() == '':
            base_slug = slugify(self.name)
            slug = base_slug

            # Проверяем уникальность slug
            counter = 1
            while Product.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        # Автоматическое определение in_stock
        if self.quantity is not None:
            self.in_stock = self.quantity > 0

        # Валидация quantity при сохранении
        if self.quantity is not None and self.quantity < 0:
            raise ValidationError(_('Quantity cannot be negative'))

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('catalog:product_detail', args=[self.slug])

    def get_breadcrumbs(self):
        """Получение хлебных крошек для товара"""
        # Получаем хлебные крошки категории
        breadcrumbs = self.category.get_breadcrumbs()

        # Добавляем товар
        breadcrumbs.append({
            'name': self.name,
            'url': self.get_absolute_url()
        })

        return breadcrumbs

    @property
    def has_discount(self):
        """Есть ли скидка на товар"""
        return self.old_price is not None and self.old_price > self.price

    @property
    def discount_percent(self):
        """Процент скидки"""
        if self.has_discount:
            return int((1 - self.price / self.old_price) * 100)
        return 0