import json
import logging

import requests
from django.core.cache import cache
from django.core.exceptions import PermissionDenied

from core.settings import FASTAPI_SERVICE_URL
# from .tasks import update_user_stats_cache
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import Purchase, News
from datetime import datetime, timedelta

from .services.fastapi_service import FastAPIService

logger = logging.getLogger(__name__)


@login_required
def dashboard_view(request):
    stats = {}
    # user_id = request.user.username
    # cache_key = f"user:stats:{user_id}"
    # stats = cache.get(cache_key)  # быстрое чтение, не блокирующее
    #
    # if stats is None:
    #     # стартуем фоновую задачу, но не ждём её результата
    #     update_user_stats_cache.delay(user_id)

    return render(
        request,
        "cabinet/dashboard.html",
        {
            "user_stats": stats or {},  # пустой словарь пока нет данных
            "loading": stats is None,
        }
    )


@login_required
def profile_view(request):
    return render(request, 'cabinet/profile.html')


@login_required
def purchases_view(request):
    purchases = Purchase.objects.filter(user=request.user).order_by('-date')
    return render(request, 'cabinet/purchases.html', {'purchases': purchases})


@login_required
def finance_view(request):
    return render(request, 'cabinet/finance.html')


# @login_required
# def refresh_stats(request):
#     """Обновление статистики по AJAX запросу"""
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             force_refresh = data.get('force', False)
#         except:
#             force_refresh = False
#
#     service = FastAPIService()
#     user_stats = service.get_user_stats(request.user.username, force_refresh=force_refresh)
#
#     if user_stats is None:
#         # Запускаем асинхронное обновление
#         task = update_user_stats_cache.delay(request.user.username)
#         return JsonResponse({
#             'status': 'updating',
#             'message': 'Данные обновляются...',
#             'task_id': str(task.id)
#         })
#
#     return JsonResponse({
#         'status': 'success',
#         'data': user_stats,
#         'refreshed': True
#     })
#
#
# @login_required
# def get_stats_json(request):
#     user_id = request.user.username
#     cache_key = f"user:stats:{user_id}"
#
#     stats = cache.get(cache_key)
#
#     if not stats:
#         update_user_stats_cache.delay(user_id)
#         return JsonResponse(
#             {"status": "loading"},
#             status=202
#         )
#
#     return JsonResponse(
#         {"status": "ok", "data": stats}
#     )


@login_required
def get_user_data(request):
    user_id = request.user.username
    try:
        r = requests.get(
            f"{FASTAPI_SERVICE_URL}/user/users/{user_id}/status",
            timeout=5
        )
        r.raise_for_status()
    except requests.RequestException as e:
        return JsonResponse(
            {"error": str(e)},
            status=503
        )

    return JsonResponse(r.json(), safe=False)



@login_required
def add_user_lo(request):
    user_id = request.user.username

    # Получаем данные из POST запроса
    if request.method == 'POST':
        try:
            # Пытаемся получить данные из JSON
            data = json.loads(request.body)
        except json.JSONDecodeError:
            # Если не JSON, пробуем получить из формы
            data = request.POST.dict()

        lo_amount = data.get('lo')

        if not lo_amount:
            return JsonResponse(
                {"error": "Параметр 'lo' не указан"},
                status=400
            )

        try:
            payload = {"lo": float(lo_amount)}

            r = requests.post(
                f"{FASTAPI_SERVICE_URL}/user/users/{user_id}/lo/add",
                json=payload,
                timeout=5
            )
            r.raise_for_status()

            return JsonResponse(r.json(), safe=False)

        except ValueError:
            return JsonResponse(
                {"error": "Параметр 'lo' должен быть числом"},
                status=400
            )
        except requests.RequestException as e:
            return JsonResponse(
                {"error": str(e)},
                status=503
            )

    # Если метод не POST
    return JsonResponse(
        {"error": "Метод не поддерживается. Используйте POST."},
        status=405
    )


@login_required
def sub_user_lo(request):
    user_id = request.user.username

    # Получаем данные из POST запроса
    if request.method == 'POST':
        try:
            # Пытаемся получить данные из JSON
            data = json.loads(request.body)
        except json.JSONDecodeError:
            # Если не JSON, пробуем получить из формы
            data = request.POST.dict()

        lo_amount = data.get('lo')

        if not lo_amount:
            return JsonResponse(
                {"error": "Параметр 'lo' не указан"},
                status=400
            )

        try:
            payload = {"lo": float(lo_amount)}

            r = requests.post(
                f"{FASTAPI_SERVICE_URL}/user/users/{user_id}/lo/subtract",
                json=payload,
                timeout=5
            )
            r.raise_for_status()

            return JsonResponse(r.json(), safe=False)

        except ValueError:
            return JsonResponse(
                {"error": "Параметр 'lo' должен быть числом"},
                status=400
            )
        except requests.RequestException as e:
            return JsonResponse(
                {"error": str(e)},
                status=503
            )

    # Если метод не POST
    return JsonResponse(
        {"error": "Метод не поддерживается. Используйте POST."},
        status=405
    )


@login_required
def get_user_team(request):
    user_id = request.user.username
    try:
        r = requests.get(
            f"{FASTAPI_SERVICE_URL}/user/users/{user_id}/structure",
            timeout=5
        )
        r.raise_for_status()
    except requests.RequestException as e:
        return JsonResponse(
            {"error": str(e)},
            status=503
        )

    return JsonResponse(r.json(), safe=False)


@login_required
def api_test_page(request):
    """Страница для тестирования API"""
    return render(request, 'cabinet/admin_api.html')


@login_required
def admin_panel(request):
    """Админ-панель для магазинов и администраторов"""
    if not request.user.can_access_admin:
        raise PermissionDenied("У вас нет доступа к админ-панели")

    return render(request, 'cabinet/admin_panel.html')