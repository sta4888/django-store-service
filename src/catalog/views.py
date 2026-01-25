from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Category, Product


def index(request):
    """Главная страница каталога"""
    categories = Category.objects.filter(parent=None, is_active=True)

    # Получаем все активные товары
    products_list = Product.active_products.all().order_by('-created_at')

    # Пагинация
    paginator = Paginator(products_list, 12)  # 12 товаров на страницу
    page = request.GET.get('page', 1)

    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        # Если page не число, показываем первую страницу
        products = paginator.page(1)
    except EmptyPage:
        # Если page вне диапазона, показываем последнюю страницу
        products = paginator.page(paginator.num_pages)

    context = {
        'categories': categories,
        'products': products,  # Теперь это Page объект
        'paginator': paginator,
    }
    return render(request, 'catalog/index.html', context)


def category_detail(request, slug):
    """Страница категории"""
    category = get_object_or_404(Category, slug=slug, is_active=True)
    products_list = Product.active_products.filter(category=category)

    # Пагинация
    paginator = Paginator(products_list, 12)
    page = request.GET.get('page', 1)

    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    context = {
        'category': category,
        'products': products,
        'paginator': paginator,
    }
    return render(request, 'catalog/category_detail.html', context)


def product_detail(request, slug):
    """Страница товара"""
    product = get_object_or_404(Product, slug=slug, is_active=True)

    # Можно добавить похожие товары из той же категории
    related_products = Product.active_products.filter(
        category=product.category
    ).exclude(pk=product.pk)[:4]

    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'catalog/product_detail.html', context)