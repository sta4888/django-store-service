import json
import logging

import requests
from django.core.cache import cache

from .tasks import update_user_stats_cache
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
    user_id = request.user.username
    cache_key = f"user:stats:{user_id}"

    stats = cache.get(cache_key)

    if not stats:
        update_user_stats_cache.delay(user_id)

    return render(
        request,
        "cabinet/dashboard.html",
        {
            "user_stats": stats,
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


@login_required
def refresh_stats(request):
    """Обновление статистики по AJAX запросу"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            force_refresh = data.get('force', False)
        except:
            force_refresh = False

    service = FastAPIService()
    user_stats = service.get_user_stats(request.user.username, force_refresh=force_refresh)

    if user_stats is None:
        # Запускаем асинхронное обновление
        task = update_user_stats_cache.delay(request.user.username)
        return JsonResponse({
            'status': 'updating',
            'message': 'Данные обновляются...',
            'task_id': str(task.id)
        })

    return JsonResponse({
        'status': 'success',
        'data': user_stats,
        'refreshed': True
    })


@login_required
def get_stats_json(request):
    user_id = request.user.username
    cache_key = f"user:stats:{user_id}"

    stats = cache.get(cache_key)

    if not stats:
        update_user_stats_cache.delay(user_id)
        return JsonResponse(
            {"status": "loading"},
            status=202
        )

    return JsonResponse(
        {"status": "ok", "data": stats}
    )


@login_required
def get_user_data(request):
    try:
        r = requests.get(
            "http://45.130.148.158:8001/user/users/00000009/status",
            timeout=5
        )
        r.raise_for_status()
    except requests.RequestException as e:
        return JsonResponse(
            {"error": str(e)},
            status=503
        )

    return JsonResponse(r.json(), safe=False)