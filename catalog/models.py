from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from mptt.models import MPTTModel, TreeForeignKey  # Импортируем MPTT


class Category(MPTTModel):  # Наследуемся от MPTTModel
    """Модель категорий товаров с древовидной структурой"""

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

    # Заменяем parent на TreeForeignKey для MPTT
    parent = TreeForeignKey(
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

    created_at = models.DateTimeField(
        _('Created at'),
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        _('Updated at'),
        auto_now=True
    )

    # MPTT-specific fields (автоматически добавляются)
    # lft, rght, tree_id, level

    class MPTTMeta:
        order_insertion_by = ['name']
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        # Показываем отступы для вложенности
        return f"{'--' * self.level} {self.name}"

    def save(self, *args, **kwargs):
        """Переопределяем save для генерации slug"""
        if not self.slug or self.slug.strip() == '':
            base_slug = slugify(self.name)
            slug = base_slug

            counter = 1
            while Category.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('catalog:category_detail', args=[self.slug])

    def get_breadcrumbs(self):
        """Получение хлебных крошек для категории через MPTT"""
        breadcrumbs = []

        # Используем get_ancestors из MPTT
        ancestors = self.get_ancestors(include_self=True)

        for ancestor in ancestors:
            breadcrumbs.append({
                'name': ancestor.name,
                'url': ancestor.get_absolute_url()
            })

        return breadcrumbs

    def get_descendants_products(self):
        """Получить все товары из этой категории и всех её подкатегорий"""
        from django.db.models import Q

        # Получаем всех потомков (включая саму категорию)
        descendants = self.get_descendants(include_self=True)

        # Получаем все товары из всех потомков
        products = Product.objects.filter(category__in=descendants)
        return products

    def get_active_children(self):
        """Получить активные дочерние категории"""
        return self.children.filter(is_active=True)

    def get_all_products_count(self):
        """Получить количество всех товаров в категории и подкатегориях"""
        return self.get_descendants_products().count()

    def get_direct_products_count(self):
        """Получить количество товаров только в этой категории"""
        return self.products.count()

    def get_tree_path(self):
        """Получить путь в виде строки: Родитель > Ребенок > Внук"""
        ancestors = self.get_ancestors(include_self=True)
        return ' > '.join([ancestor.name for ancestor in ancestors])

    @property
    def is_root(self):
        """Является ли категория корневой (уровень 0)"""
        return self.level == 0

    @property
    def has_children(self):
        """Есть ли у категории дети"""
        return self.children.exists()


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
        breadcrumbs = self.category.get_breadcrumbs()  # Используем метод категории

        # Добавляем сам товар
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
