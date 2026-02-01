import pytest
from django.core.exceptions import ValidationError


@pytest.mark.django_db
def test_create_category():
    """Тест создания категории"""
    from catalog.models import Category

    category = Category.objects.create(
        name='Электроника',
        slug='electronics',  # ← указываем slug явно
        description='Электронные товары'
    )

    assert category.name == 'Электроника'
    assert category.slug == 'electronics'
    assert category.description == 'Электронные товары'
    assert category.is_active is True
    assert category.parent is None


@pytest.mark.django_db
def test_category_tree():
    """Тест древовидной структуры категорий"""
    from catalog.models import Category

    # Создаём корневую категорию
    root = Category.objects.create(
        name='Каталог',
        slug='catalog',
        is_root=True
    )

    # Создаём дочернюю категорию
    child = Category.objects.create(
        name='Электроника',
        slug='electronics',
        parent=root
    )

    assert child.parent == root
    assert child in root.children.all()

    # Проверяем уровень вложенности (упрощённо)
    level = 0
    parent = child.parent
    while parent:
        level += 1
        parent = parent.parent
    assert level == 1  # Уровень вложенности


@pytest.mark.django_db
def test_category_slug_auto_generation():
    """Тест авто-генерации slug"""
    from catalog.models import Category

    category = Category.objects.create(
        name='Смартфоны и гаджеты'
        # slug не указываем - должен сгенерироваться автоматически
    )

    assert category.slug is not None
    assert category.slug != ''
    # Проверяем что slug содержит транслитерированное название
    assert 'smartfony' in category.slug or 'gadzhety' in category.slug


@pytest.mark.django_db
def test_create_product():
    """Тест создания товара"""
    from catalog.models import Category, Product

    # Сначала создаём категорию
    category = Category.objects.create(
        name='Электроника',
        slug='electronics'
    )

    # Создаём товар
    product = Product.objects.create(
        name='iPhone 13',
        slug='iphone-13',  # ← указываем slug явно
        category=category,
        price=79999.99,
        sku='IPH13-256-BLK',
        description='Смартфон Apple',
        short_description='Новый iPhone',
        quantity=10
    )

    assert product.name == 'iPhone 13'
    assert product.slug == 'iphone-13'
    assert product.category == category
    assert product.price == 79999.99
    assert product.sku == 'IPH13-256-BLK'
    assert product.quantity == 10
    assert product.in_stock is True
    assert product.is_active is True


@pytest.mark.django_db
def test_product_slug_auto_generation():
    """Тест авто-генерации slug для товара"""
    from catalog.models import Category, Product

    category = Category.objects.create(name='Тест', slug='test')

    product = Product.objects.create(
        name='Тестовый товар с русским названием',
        category=category,
        price=1000
        # slug не указываем - должен сгенерироваться
    )

    assert product.slug is not None
    assert product.slug != ''
    # Проверяем что slug не пустой и уникальный


@pytest.mark.django_db
def test_product_attributes():
    """Тест добавления атрибутов к товару"""
    from catalog.models import Category, Product, Attribute, AttributeValue

    category = Category.objects.create(name='Тест', slug='test')
    product = Product.objects.create(
        name='Тестовый товар',
        slug='test-product',  # ← указываем slug
        category=category,
        price=1000
    )

    # Создаём атрибут и значение
    color_attr = Attribute.objects.create(
        name='Цвет',
        code='color',
        filter_type='multi'
    )

    red_value = AttributeValue.objects.create(
        attribute=color_attr,
        value='Красный',
        code='red'
    )

    # Добавляем атрибут к товару
    product.attributes.add(red_value)

    assert red_value in product.attributes.all()
    assert product in red_value.products.all()


@pytest.mark.django_db
def test_product_active_manager():
    """Тест менеджера активных товаров"""
    from catalog.models import Category, Product

    category = Category.objects.create(
        name='Активная категория',
        slug='active-category'
    )

    # Создаём активный товар
    active_product = Product.objects.create(
        name='Активный товар 1',
        slug='active-product-1',
        category=category,
        price=1000,
        is_active=True,
        quantity=10
    )

    # Создаём неактивный товар
    inactive_product = Product.objects.create(
        name='Неактивный товар',
        slug='inactive-product',
        category=category,
        price=1000,
        is_active=False,
        quantity=5
    )

    # Создаём неактивную категорию
    inactive_category = Category.objects.create(
        name='Неактивная категория',
        slug='inactive-category',
        is_active=False
    )

    # Товар в неактивной категории
    product_in_inactive_category = Product.objects.create(
        name='Товар в неактивной категории',
        slug='product-in-inactive',
        category=inactive_category,
        price=1000,
        is_active=True,
        quantity=3
    )

    # Получаем активные товары через менеджер
    active_products = Product.active_products.all()

    assert active_product in active_products
    assert inactive_product not in active_products
    assert product_in_inactive_category not in active_products


@pytest.mark.django_db
def test_product_in_stock_logic():
    """Тест логики наличия товара"""
    from catalog.models import Category, Product

    category = Category.objects.create(name='Тест', slug='test-category')

    # Товар с количеством > 0
    in_stock_product = Product.objects.create(
        name='В наличии',
        slug='in-stock-product',
        category=category,
        price=1000,
        quantity=5
    )

    # Товар с количеством = 0
    out_of_stock_product = Product.objects.create(
        name='Нет в наличии',
        slug='out-of-stock-product',
        category=category,
        price=1000,
        quantity=0
    )

    # Товар с отрицательным количеством (проверяем валидацию)
    product_with_negative = Product(
        name='Ошибка',
        slug='error-product',
        category=category,
        price=1000,
        quantity=-1
    )

    # Проверяем что save() вызывает ValidationError
    with pytest.raises(ValidationError):
        product_with_negative.save()

    assert in_stock_product.in_stock is True
    assert out_of_stock_product.in_stock is False