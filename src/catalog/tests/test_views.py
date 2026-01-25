import pytest
from django.urls import reverse
from catalog.models import Category, Product


@pytest.mark.django_db
class TestCatalogViews:
    """Тесты views каталога"""

    @pytest.fixture
    def create_test_data(self):
        """Создаём тестовые данные"""
        # Создаём категории
        category1 = Category.objects.create(name='Категория 1', slug='category-1')
        category2 = Category.objects.create(name='Категория 2', slug='category-2')

        # Создаём 15 товаров в каждой категории
        products = []
        for i in range(15):
            product1 = Product.objects.create(
                name=f'Товар {i} Кат1',
                slug=f'product-{i}-cat1',
                category=category1,
                price=100 * (i + 1),
                quantity=10
            )
            product2 = Product.objects.create(
                name=f'Товар {i} Кат2',
                slug=f'product-{i}-cat2',
                category=category2,
                price=200 * (i + 1),
                quantity=5
            )
            products.extend([product1, product2])

        return {
            'category1': category1,
            'category2': category2,
            'products': products
        }

    def test_index_view(self, client, create_test_data):
        """Тест главной страницы каталога"""
        url = reverse('catalog:index')
        response = client.get(url)

        assert response.status_code == 200
        assert 'Каталог товаров' in response.content.decode()
        assert 'products' in response.context

        # Проверяем пагинацию (должно быть 2 страницы: 30 товаров / 12 на страницу)
        products = response.context['products']
        assert products.paginator.num_pages == 3  # 30/12 = 2.5 → 3 страницы
        assert len(products) == 12  # Первая страница

    def test_index_pagination(self, client, create_test_data):
        """Тест пагинации на главной"""
        # Страница 1
        response = client.get(reverse('catalog:index') + '?page=1')
        assert response.status_code == 200
        products = response.context['products']
        assert products.number == 1

        # Страница 2
        response = client.get(reverse('catalog:index') + '?page=2')
        assert response.status_code == 200
        products = response.context['products']
        assert products.number == 2

        # Страница 3 (последняя)
        response = client.get(reverse('catalog:index') + '?page=3')
        assert response.status_code == 200
        products = response.context['products']
        assert products.number == 3
        assert len(products) == 6  # 30 - 12*2 = 6 товаров на последней странице

    def test_category_detail_view(self, client, create_test_data):
        """Тест страницы категории"""
        category = create_test_data['category1']
        url = reverse('catalog:category_detail', args=[category.slug])
        response = client.get(url)

        assert response.status_code == 200
        assert category.name in response.content.decode()
        assert 'products' in response.context

        # В категории 15 товаров, на странице 12
        products = response.context['products']
        assert products.paginator.count == 15
        assert products.paginator.num_pages == 2  # 15/12 = 1.25 → 2 страницы

    def test_product_detail_view(self, client, create_test_data):
        """Тест страницы товара"""
        product = create_test_data['products'][0]
        url = reverse('catalog:product_detail', args=[product.slug])
        response = client.get(url)

        assert response.status_code == 200
        assert product.name in response.content.decode()
        assert 'product' in response.context
        assert response.context['product'] == product

    def test_invalid_page_number(self, client, create_test_data):
        """Тест неверного номера страницы"""
        # Слишком большой номер
        response = client.get(reverse('catalog:index') + '?page=999')
        assert response.status_code == 200
        # Должна показываться последняя страница
        products = response.context['products']
        assert products.number == products.paginator.num_pages

        # Некорректный номер (не число)
        response = client.get(reverse('catalog:index') + '?page=abc')
        assert response.status_code == 200
        # Должна показываться первая страница
        products = response.context['products']
        assert products.number == 1

    def test_empty_category(self, client):
        """Тест пустой категории"""
        category = Category.objects.create(name='Пустая категория', slug='empty-category')
        url = reverse('catalog:category_detail', args=[category.slug])
        response = client.get(url)

        assert response.status_code == 200
        assert 'нет товаров' in response.content.decode()

    def test_inactive_category(self, client):
        """Тест неактивной категории (должна возвращать 404)"""
        category = Category.objects.create(
            name='Неактивная категория',
            slug='inactive-category',
            is_active=False
        )
        url = reverse('catalog:category_detail', args=[category.slug])
        response = client.get(url)

        assert response.status_code == 404

    def test_inactive_product(self, client, create_test_data):
        """Тест неактивного товара (должен возвращать 404)"""
        product = create_test_data['products'][0]
        product.is_active = False
        product.save()

        url = reverse('catalog:product_detail', args=[product.slug])
        response = client.get(url)

        assert response.status_code == 404