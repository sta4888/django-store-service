from django import forms
from django.db.models import Min, Max
from .models import Attribute, AttributeValue, Category


class ProductFilterForm(forms.Form):
    """Форма фильтрации товаров для главной страницы"""

    # Фильтр по цене
    min_price = forms.DecimalField(
        required=False,
        min_value=0,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'От'
        })
    )

    max_price = forms.DecimalField(
        required=False,
        min_value=0,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'До'
        })
    )

    # Фильтр по наличию
    in_stock = forms.BooleanField(
        required=False,
        label='Только в наличии',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    # Фильтр по категории (для главной страницы)
    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(is_active=True),
        required=False,
        empty_label='Все категории',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    # Сортировка
    SORT_CHOICES = [
        ('', 'По умолчанию'),
        ('price_asc', 'Цена (по возрастанию)'),
        ('price_desc', 'Цена (по убыванию)'),
        ('name_asc', 'Название (А-Я)'),
        ('name_desc', 'Название (Я-А)'),
        ('newest', 'Сначала новые'),
    ]

    sort_by = forms.ChoiceField(
        choices=SORT_CHOICES,
        required=False,
        initial='',
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class CategoryFilterForm(ProductFilterForm):
    """Форма фильтрации для страницы категории (с атрибутами)"""

    def __init__(self, *args, **kwargs):
        self.category = kwargs.pop('category', None)
        super().__init__(*args, **kwargs)

        # Убираем поле категории для страницы категории
        self.fields.pop('category', None)

        # Динамически добавляем поля для атрибутов
        if self.category:
            self.add_attribute_fields()

    def add_attribute_fields(self):
        """Добавление полей для атрибутов категории"""
        from .models import Product

        # Получаем товары этой категории и подкатегорий
        descendants = self.category.get_descendants(include_self=True)
        products = Product.objects.filter(category__in=descendants, is_active=True)

        # Атрибуты с множественным выбором
        multi_attrs = Attribute.objects.filter(
            filter_type='multi',
            values__products__in=products
        ).distinct()

        for attr in multi_attrs:
            values = AttributeValue.objects.filter(
                attribute=attr,
                products__in=products
            ).distinct().order_by('order', 'value')

            if values.exists():
                self.fields[f'attr_{attr.code}'] = forms.MultipleChoiceField(
                    choices=[(v.id, v.value) for v in values],
                    required=False,
                    widget=forms.CheckboxSelectMultiple(attrs={
                        'class': 'form-check-input attribute-filter',
                        'data-attribute': attr.code
                    }),
                    label=attr.name
                )