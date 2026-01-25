import pytest


@pytest.mark.django_db
def test_basic_category():
    """Базовый тест категории"""
    from catalog.models import Category

    # Создаём с явным slug
    category = Category.objects.create(
        name='Тест',
        slug='test-category'
    )

    assert category.name == 'Тест'
    assert category.slug == 'test-category'
    assert category.is_active is True


@pytest.mark.django_db
def test_basic_product():
    """Базовый тест товара"""
    from catalog.models import Category, Product

    category = Category.objects.create(
        name='Категория',
        slug='category'
    )

    product = Product.objects.create(
        name='Товар',
        slug='product',
        category=category,
        price=1000,
        quantity=5
    )

    assert product.name == 'Товар'
    assert product.slug == 'product'
    assert product.category == category
    assert product.price == 1000
    assert product.quantity == 5
    assert product.in_stock is True


@pytest.mark.django_db
def test_product_without_slug():
    """Тест товара без указания slug"""
    from catalog.models import Category, Product

    category = Category.objects.create(
        name='Категория',
        slug='category-2'
    )

    # Первый товар без slug
    product1 = Product.objects.create(
        name='Товар 1',
        category=category,
        price=1000
    )

    # Второй товар без slug (должен получить уникальный)
    product2 = Product.objects.create(
        name='Товар 2',
        category=category,
        price=2000
    )

    assert product1.slug is not None
    assert product1.slug != ''
    assert product2.slug is not None
    assert product2.slug != ''
    assert product1.slug != product2.slug  # Должны быть разными