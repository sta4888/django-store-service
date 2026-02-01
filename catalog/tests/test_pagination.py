import pytest
from django.core.paginator import Paginator, Page, EmptyPage, PageNotAnInteger
from catalog.models import Category, Product


@pytest.mark.django_db
class TestPagination:
    """Тесты пагинации"""

    @pytest.fixture
    def create_test_products(self):
        """Создаём тестовые товары"""
        category = Category.objects.create(name='Тест', slug='test')

        # Создаём 25 товаров
        products = []
        for i in range(25):
            product = Product.objects.create(
                name=f'Товар {i}',
                slug=f'product-{i}',
                category=category,
                price=100 * (i + 1),
                quantity=10
            )
            products.append(product)

        return products

    def test_paginator_creation(self, create_test_products):
        """Тест создания пагинатора"""
        products = create_test_products

        paginator = Paginator(products, 10)  # 10 товаров на страницу

        assert paginator.count == 25
        assert paginator.num_pages == 3  # 25/10 = 3 страницы
        assert paginator.per_page == 10

    def test_page_objects(self, create_test_products):
        """Тест объектов страницы"""
        products = create_test_products
        paginator = Paginator(products, 10)

        page1 = paginator.page(1)
        page2 = paginator.page(2)
        page3 = paginator.page(3)

        assert isinstance(page1, Page)
        assert len(page1.object_list) == 10
        assert len(page2.object_list) == 10
        assert len(page3.object_list) == 5  # На последней странице 5 товаров

        # Проверяем номера товаров на страницах
        assert page1.object_list[0].name == 'Товар 0'
        assert page1.object_list[9].name == 'Товар 9'
        assert page2.object_list[0].name == 'Товар 10'

    def test_page_validation(self, create_test_products):
        """Тест валидации номеров страниц"""
        products = create_test_products
        paginator = Paginator(products, 10)

        # Проверяем что несуществующая страница вызывает ошибку
        with pytest.raises(PageNotAnInteger):
            paginator.page('abc')

        with pytest.raises(PageNotAnInteger):
            paginator.page(3.14)

        with pytest.raises(EmptyPage):
            paginator.page(0)  # Нумерация с 1

        with pytest.raises(EmptyPage):
            paginator.page(4)  # Всего 3 страницы

        with pytest.raises(EmptyPage):
            paginator.page(999)

    def test_page_methods(self, create_test_products):
        """Тест методов страницы"""
        products = create_test_products
        paginator = Paginator(products, 10)
        page2 = paginator.page(2)

        assert page2.has_next() is True
        assert page2.has_previous() is True
        assert page2.has_other_pages() is True
        assert page2.next_page_number() == 3
        assert page2.previous_page_number() == 1

        page1 = paginator.page(1)
        assert page1.has_previous() is False
        # Для первой страницы previous_page_number должен вызывать EmptyPage
        with pytest.raises(EmptyPage):
            page1.previous_page_number()

        page3 = paginator.page(3)
        assert page3.has_next() is False
        # Для последней страницы next_page_number должен вызывать EmptyPage
        with pytest.raises(EmptyPage):
            page3.next_page_number()

    def test_custom_per_page(self, create_test_products):
        """Тест разного количества элементов на странице"""
        products = create_test_products

        # 5 на страницу
        paginator5 = Paginator(products, 5)
        assert paginator5.num_pages == 5

        # 20 на страницу
        paginator20 = Paginator(products, 20)
        assert paginator20.num_pages == 2  # 20+5

        # Все на одной странице
        paginator_all = Paginator(products, 100)
        assert paginator_all.num_pages == 1