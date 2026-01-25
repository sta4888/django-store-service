from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Category, Product


def index(request):
    """Главная страница каталога"""
    categories = Category.objects.filter(parent=None, is_active=True)
    products = Product.active_products.all()[:12]  # Последние 12 товаров

    context = {
        'categories': categories,
        'products': products,
    }
    return render(request, 'catalog/index.html', context)


def category_detail(request, slug):
    """Страница категории"""
    category = get_object_or_404(Category, slug=slug, is_active=True)
    products = Product.active_products.filter(category=category)

    context = {
        'category': category,
        'products': products,
    }
    return render(request, 'catalog/category_detail.html', context)


def product_detail(request, slug):
    """Страница товара"""
    product = get_object_or_404(Product, slug=slug, is_active=True)

    context = {
        'product': product,
    }
    return render(request, 'catalog/product_detail.html', context)