from django import template
from django.urls import reverse

register = template.Library()


@register.inclusion_tag('catalog/includes/breadcrumbs.html', takes_context=True)
def show_breadcrumbs(context, obj=None):
    """
    Шаблонный тег для отображения хлебных крошек.

    Использование в шаблоне:
    {% load breadcrumbs %}
    {% show_breadcrumbs product %}
    или
    {% show_breadcrumbs category %}
    """
    request = context.get('request')
    breadcrumbs = []

    # Если объект передан явно
    if obj and hasattr(obj, 'get_breadcrumbs'):
        breadcrumbs = obj.get_breadcrumbs()

    # Если нет объекта, пробуем получить из контекста
    elif not breadcrumbs:
        # Пробуем найти объект в контексте
        for key in ['product', 'category', 'object']:
            if key in context:
                obj = context[key]
                if hasattr(obj, 'get_breadcrumbs'):
                    breadcrumbs = obj.get_breadcrumbs()
                    break

    # Добавляем домашнюю страницу в начало
    if breadcrumbs:
        if request and request.user.is_authenticated:
            home_name = 'Кабинет'
            home_url = reverse('cabinet:dashboard')  # проверь namespace
        else:
            home_name = 'Главная'
            home_url = reverse('catalog:index')  # или pages:home

        if breadcrumbs[0]['url'] != home_url:
            breadcrumbs.insert(0, {
                'name': home_name,
                'url': home_url,
            })

    return {
        'breadcrumbs': breadcrumbs,
        'request': request
    }


@register.simple_tag(takes_context=True)
def get_breadcrumbs(context, obj=None):
    """
    Простой тег для получения хлебных крошек как списка.
    Возвращает список для использования в других тегах.
    """
    if obj and hasattr(obj, 'get_breadcrumbs'):
        return obj.get_breadcrumbs()

    # Пробуем найти объект в контексте
    for key in ['product', 'category', 'object']:
        if key in context:
            obj = context[key]
            if hasattr(obj, 'get_breadcrumbs'):
                return obj.get_breadcrumbs()

    return []