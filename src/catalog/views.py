# catalog/views.py
from django.shortcuts import get_object_or_404, render
from django.db.models import Q, Min, Max
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import ProductFilterForm, CategoryFilterForm  # Добавьте этот импорт
from .models import Category, Product


def index(request):
    """Главная страница каталога со всеми товарами"""
    products = Product.objects.filter(is_active=True).select_related('category')

    # Форма фильтрации
    filter_form = ProductFilterForm(request.GET)

    if filter_form.is_valid():
        # Фильтр по категории
        category = filter_form.cleaned_data.get('category')
        if category:
            descendants = category.get_descendants(include_self=True)
            products = products.filter(category__in=descendants)

        # Фильтр по цене
        min_price = filter_form.cleaned_data.get('min_price')
        max_price = filter_form.cleaned_data.get('max_price')

        if min_price:
            products = products.filter(price__gte=min_price)
        if max_price:
            products = products.filter(price__lte=max_price)

        # Фильтр по наличию
        if filter_form.cleaned_data.get('in_stock'):
            products = products.filter(in_stock=True)

        # Сортировка
        sort_by = filter_form.cleaned_data.get('sort_by')
        if sort_by == 'price_asc':
            products = products.order_by('price')
        elif sort_by == 'price_desc':
            products = products.order_by('-price')
        elif sort_by == 'name_asc':
            products = products.order_by('name')
        elif sort_by == 'name_desc':
            products = products.order_by('-name')
        elif sort_by == 'newest':
            products = products.order_by('-created_at')

    # Пагинация
    page_size = request.GET.get('page_size', 12)
    paginator = Paginator(products, page_size)
    page = request.GET.get('page')

    try:
        products_page = paginator.page(page)
    except PageNotAnInteger:
        products_page = paginator.page(1)
    except EmptyPage:
        products_page = paginator.page(paginator.num_pages)

    # Диапазон цен для отображения
    price_range = products.aggregate(
        min_price=Min('price'),
        max_price=Max('price')
    )

    context = {
        'categories': Category.objects.filter(parent=None, is_active=True),
        'products': products_page,
        'filter_form': filter_form,
        'price_range': price_range,
        'page_size': int(page_size),
        'paginator': paginator,
    }
    return render(request, 'catalog/index.html', context)


def category_detail(request, slug):
    """Детальная страница категории"""
    category = get_object_or_404(Category, slug=slug)

    # Получаем товары категории и подкатегорий
    descendants = category.get_descendants(include_self=True)
    products = Product.objects.filter(
        category__in=descendants,
        is_active=True
    ).select_related('category').prefetch_related('attributes')

    # Форма фильтрации для категории
    filter_form = CategoryFilterForm(request.GET, category=category)  # Используйте CategoryFilterForm

    if filter_form.is_valid():
        # Фильтр по цене
        min_price = filter_form.cleaned_data.get('min_price')
        max_price = filter_form.cleaned_data.get('max_price')

        if min_price:
            products = products.filter(price__gte=min_price)
        if max_price:
            products = products.filter(price__lte=max_price)

        # Фильтр по наличию
        if filter_form.cleaned_data.get('in_stock'):
            products = products.filter(in_stock=True)

        # Фильтр по атрибутам
        for field_name, value in filter_form.cleaned_data.items():
            if field_name.startswith('attr_') and value:
                products = products.filter(attributes__id__in=value).distinct()

        # Сортировка
        sort_by = filter_form.cleaned_data.get('sort_by')
        if sort_by == 'price_asc':
            products = products.order_by('price')
        elif sort_by == 'price_desc':
            products = products.order_by('-price')
        elif sort_by == 'name_asc':
            products = products.order_by('name')
        elif sort_by == 'name_desc':
            products = products.order_by('-name')
        elif sort_by == 'newest':
            products = products.order_by('-created_at')

    # Пагинация
    page_size = request.GET.get('page_size', 12)
    paginator = Paginator(products, page_size)
    page = request.GET.get('page')

    try:
        products_page = paginator.page(page)
    except PageNotAnInteger:
        products_page = paginator.page(1)
    except EmptyPage:
        products_page = paginator.page(paginator.num_pages)

    # Диапазон цен для отображения
    price_range = products.aggregate(
        min_price=Min('price'),
        max_price=Max('price')
    )

    context = {
        'category': category,
        'products': products_page,
        'filter_form': filter_form,
        'price_range': price_range,
        'page_size': int(page_size),
        'paginator': paginator,
        'subcategories': category.get_children().filter(is_active=True),
    }
    return render(request, 'catalog/category_detail.html', context)


def product_detail(request, slug):
    """Детальная страница товара"""
    product = get_object_or_404(
        Product.objects.select_related('category').prefetch_related('attributes'),
        slug=slug,
        is_active=True
    )

    # Рекомендуемые товары (из той же категории)
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id)[:4]

    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'catalog/product_detail.html', context)