from django.urls import resolve, Resolver404


def breadcrumbs(request):
    """
    Контекстный процессор для автоматического добавления хлебных крошек.
    Определяет текущий объект на основе URL и добавляет его хлебные крошки в контекст.
    """
    from catalog.models import Category, Product

    breadcrumbs_list = []

    try:
        # Пытаемся определить что за страница
        resolver_match = resolve(request.path_info)

        # Если это страница категории
        if resolver_match.url_name == 'category_detail':
            slug = resolver_match.kwargs.get('slug')
            if slug:
                try:
                    category = Category.objects.get(slug=slug)
                    breadcrumbs_list = category.get_breadcrumbs()
                except Category.DoesNotExist:
                    pass

        # Если это страница товара
        elif resolver_match.url_name == 'product_detail':
            slug = resolver_match.kwargs.get('slug')
            if slug:
                try:
                    product = Product.objects.get(slug=slug)
                    breadcrumbs_list = product.get_breadcrumbs()
                except Product.DoesNotExist:
                    pass

        # Если это главная каталога
        elif resolver_match.url_name == 'index':
            breadcrumbs_list = [{
                'name': 'Каталог',
                'url': request.path
            }]

    except Resolver404:
        # Если URL не найден, ничего не добавляем
        pass

    return {
        'breadcrumbs': breadcrumbs_list
    }