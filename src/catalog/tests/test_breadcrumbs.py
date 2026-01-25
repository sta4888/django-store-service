import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_category_breadcrumbs():
    """Тест хлебных крошек для категории"""
    from catalog.models import Category

    # Создаём иерархию категорий
    root = Category.objects.create(
        name='Каталог',
        slug='catalog',
        is_root=True
    )

    electronics = Category.objects.create(
        name='Электроника',
        slug='electronics',
        parent=root
    )

    phones = Category.objects.create(
        name='Телефоны',
        slug='phones',
        parent=electronics
    )

    # Получаем хлебные крошки для категории phones
    breadcrumbs = phones.get_breadcrumbs()

    assert len(breadcrumbs) == 3

    # Проверяем имена
    assert breadcrumbs[0]['name'] == 'Каталог'
    assert breadcrumbs[1]['name'] == 'Электроника'
    assert breadcrumbs[2]['name'] == 'Телефоны'

    # Проверяем URL (без reverse, просто проверяем что они есть)
    assert 'url' in breadcrumbs[0]
    assert 'url' in breadcrumbs[1]
    assert 'url' in breadcrumbs[2]


@pytest.mark.django_db
def test_product_breadcrumbs():
    """Тест хлебных крошек для товара"""
    from catalog.models import Category, Product

    # Создаём иерархию
    root = Category.objects.create(
        name='Каталог',
        slug='catalog',
        is_root=True
    )

    electronics = Category.objects.create(
        name='Электроника',
        slug='electronics',
        parent=root
    )

    phones = Category.objects.create(
        name='Телефоны',
        slug='phones',
        parent=electronics
    )

    # Создаём товар
    product = Product.objects.create(
        name='iPhone 13',
        slug='iphone-13',
        category=phones,
        price=79999
    )

    # Получаем хлебные крошки для товара
    breadcrumbs = product.get_breadcrumbs()

    assert len(breadcrumbs) == 4

    # Проверяем имена
    assert breadcrumbs[0]['name'] == 'Каталог'
    assert breadcrumbs[1]['name'] == 'Электроника'
    assert breadcrumbs[2]['name'] == 'Телефоны'
    assert breadcrumbs[3]['name'] == 'iPhone 13'


@pytest.mark.django_db
def test_root_category_breadcrumbs():
    """Тест хлебных крошек для корневой категории"""
    from catalog.models import Category

    root = Category.objects.create(
        name='Каталог',
        slug='catalog',
        is_root=True
    )

    breadcrumbs = root.get_breadcrumbs()

    assert len(breadcrumbs) == 1
    assert breadcrumbs[0]['name'] == 'Каталог'
    assert 'url' in breadcrumbs[0]


@pytest.mark.django_db
def test_category_without_parent():
    """Тест категории без родителя"""
    from catalog.models import Category

    category = Category.objects.create(
        name='Категория',
        slug='category'
    )

    breadcrumbs = category.get_breadcrumbs()

    # Категория без родителя и без is_root
    assert len(breadcrumbs) == 2  # Каталог + категория
    assert breadcrumbs[0]['name'] == 'Каталог'
    assert breadcrumbs[1]['name'] == 'Категория'
    assert 'url' in breadcrumbs[0]
    assert 'url' in breadcrumbs[1]