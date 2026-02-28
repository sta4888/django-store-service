import json
import logging

import requests
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from core.settings import FASTAPI_SERVICE_URL
# from .tasks import update_user_stats_cache
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import Purchase, News
from datetime import datetime, timedelta
from accounts.models import CustomUser

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
    # user_id = request.user.username

    # Получаем данные из POST запроса
    if request.method == 'POST':
        try:
            # Пытаемся получить данные из JSON
            data = json.loads(request.body)
        except json.JSONDecodeError:
            # Если не JSON, пробуем получить из формы
            data = request.POST.dict()

        lo_amount = data.get('lo')
        user_id = data.get('user_id')

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
    # user_id = request.user.username

    # Получаем данные из POST запроса
    if request.method == 'POST':
        try:
            # Пытаемся получить данные из JSON
            data = json.loads(request.body)
        except json.JSONDecodeError:
            # Если не JSON, пробуем получить из формы
            data = request.POST.dict()

        lo_amount = data.get('lo')
        user_id = data.get('user_id')

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


@login_required
def structure_view(request):
    """Страница структуры рефералов пользователя"""
    user = request.user
    
    # Получаем рефералов первого уровня
    direct_referrals = CustomUser.objects.filter(
        referrer=user
    ).select_related('referrer').order_by('-date_joined')
    
    # Пагинация
    paginator = Paginator(direct_referrals, 20)  # 20 записей на страницу
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Получаем общую статистику
    total_referrals = user.total_referrals
    active_referrals = user.active_referrals
    group_volume = user.group_volume
    
    context = {
        'direct_referrals': page_obj,
        'total_referrals': total_referrals,
        'active_referrals': active_referrals,
        'group_volume': group_volume,
    }
    
    return render(request, 'cabinet/structure.html', context)


# Дополнительная функция для AJAX-загрузки рефералов (по желанию)
@login_required
def get_referrals_json(request):
    """Получение списка рефералов в формате JSON с данными из API"""
    user = request.user
    level = request.GET.get('level', '1')
    
    try:
        level = int(level)
    except ValueError:
        level = 1
    
    try:
        # Получаем структуру из FastAPI
        response = requests.get(
            f"{FASTAPI_SERVICE_URL}/user/users/{user.username}/structure",
            timeout=5
        )
        response.raise_for_status()
        api_data = response.json()
        
        if api_data.get('error'):
            return JsonResponse({
                'error': True,
                'message': api_data.get('error_msg', 'Ошибка при получении данных')
            }, status=500)
            
        structure_data = api_data.get('data', {})
        team_members = structure_data.get('team', [])
        
    except requests.RequestException as e:
        logger.error(f"Ошибка API при получении структуры: {e}")
        return JsonResponse({
            'error': True,
            'message': str(e)
        }, status=503)
    
    # Получаем данные из БД
    referral_user_ids = [str(member.get('user_id')) for member in team_members]
    db_referrals = CustomUser.objects.filter(user_id__in=referral_user_ids)
    db_referrals_dict = {str(ref.user_id): ref for ref in db_referrals}
    
    # Обрабатываем только первый уровень
    if level == 1:
        referrals_data = []
        for api_member in team_members:
            user_id = str(api_member.get('user_id'))
            db_data = db_referrals_dict.get(user_id)
            
            if db_data:
                member_data = {
                    'id': user_id,
                    'name': db_data.get_full_name() or db_data.username,
                    'email': db_data.email,
                    'phone': db_data.phone,
                    'country': db_data.country,
                    'registration_date': db_data.date_joined.strftime('%d.%m.%Y'),
                    'personal_volume': float(api_member.get('lo', 0)),  # Из API
                    'group_volume': float(db_data.group_volume),  # Из БД
                    'partner_level': db_data.partner_level,
                    'user_type': db_data.user_type,
                    'total_referrals': db_data.total_referrals,
                    'active_referrals': db_data.active_referrals,
                    'earnings': float(db_data.earnings),
                    'team_count': len(api_member.get('team', [])),
                }
                referrals_data.append(member_data)
        
        return JsonResponse({
            'level': level,
            'referrals': referrals_data,
            'total_count': len(referrals_data),
            'error': False
        })
    
    # Для второго уровня и глубже (рекурсивно)
    elif level > 1:
        all_referrals_data = []
        
        def get_deep_referrals(members, current_level, max_level):
            if current_level > max_level:
                return []
            
            referrals_data = []
            for member in members:
                user_id = str(member.get('user_id'))
                
                try:
                    # Получаем структуру для каждого члена команды
                    member_response = requests.get(
                        f"{FASTAPI_SERVICE_URL}/user/users/{user_id}/structure",
                        timeout=3
                    )
                    if member_response.status_code == 200:
                        member_data = member_response.json()
                        if not member_data.get('error'):
                            # Получаем данные из БД
                            try:
                                db_data = CustomUser.objects.get(user_id=user_id)
                            except CustomUser.DoesNotExist:
                                db_data = None
                            
                            member_info = {
                                'id': user_id,
                                'level': current_level,
                                'personal_volume': float(member.get('lo', 0)),
                                'team_count': len(member.get('team', [])),
                            }
                            
                            if db_data:
                                member_info.update({
                                    'name': db_data.get_full_name() or db_data.username,
                                    'email': db_data.email,
                                    'phone': db_data.phone,
                                    'registration_date': db_data.date_joined.strftime('%d.%m.%Y'),
                                    'group_volume': float(db_data.group_volume),
                                    'partner_level': db_data.partner_level,
                                })
                            
                            referrals_data.append(member_info)
                            
                            # Рекурсивно получаем команду
                            if current_level < max_level:
                                sub_team = member_data.get('data', {}).get('team', [])
                                referrals_data.extend(
                                    get_deep_referrals(sub_team, current_level + 1, max_level)
                                )
                except:
                    continue
            
            return referrals_data
        
        # Начинаем рекурсию с команды первого уровня
        deep_referrals = get_deep_referrals(team_members, 2, level)
        
        return JsonResponse({
            'level': level,
            'referrals': deep_referrals,
            'total_count': len(deep_referrals),
            'error': False
        })
    
    return JsonResponse({
        'level': level,
        'referrals': [],
        'total_count': 0,
        'error': False
    })



@login_required
def referral_tree_api(request):
    """
    Возвращает дерево рефералов для текущего пользователя.
    Без учёта глубины — загружает всю структуру целиком.
    """
    nodes = []
    edges = []
    visited = set()  # защита от циклов

    def get_short_name(user):
        parts = [user.first_name, user.last_name]
        name = ' '.join(p for p in parts if p).strip()
        return name or user.username

    def get_full_name(user):
        parts = [user.last_name, user.first_name, getattr(user, 'middle_name', '')]
        name = ' '.join(p for p in parts if p).strip()
        return name or user.username

    def traverse(user, level):
        if user.pk in visited:
            return
        visited.add(user.pk)

        nodes.append({
            'id':              user.user_id,
            'label':           get_short_name(user),
            'title':           get_full_name(user),   # для тултипа
            'level':           level,
            'active':          getattr(user, 'is_active', True),
            'personal_volume': float(getattr(user, 'personal_volume', 0) or 0),
            'group_volume':    float(getattr(user, 'group_volume', 0) or 0),
            'partner_level':   getattr(user, 'partner_level', ''),
            'total_referrals': getattr(user, 'total_referrals', 0),
            'user_type':       getattr(user, 'user_type', 'partner'),
        })

        # Загружаем прямых рефералов одним запросом
        referrals = CustomUser.objects.filter(referrer=user)

        for referral in referrals:
            edges.append({'from': user.user_id, 'to': referral.user_id})
            traverse(referral, level + 1)

    # Стартуем с текущего пользователя
    traverse(request.user, level=0)

    return JsonResponse({'nodes': nodes, 'edges': edges})



@login_required
def get_referral_details(request, user_id):
    """Получение детальной информации о реферале"""
    try:
        # Проверяем, что пользователь существует
        db_user = CustomUser.objects.get(user_id=user_id)
        
        # Проверяем, что это реферал текущего пользователя
        if db_user.referrer != request.user:
            return JsonResponse({'error': True, 'message': 'Доступ запрещен'}, status=403)
        
        # Получаем данные из API
        try:
            response = requests.get(
                f"{FASTAPI_SERVICE_URL}/user/users/{user_id}/status",
                timeout=5
            )
            if response.status_code == 200:
                api_data = response.json()
                lo_amount = api_data.get('lo', 0)
            else:
                lo_amount = 0
        except:
            lo_amount = 0
        
        data = {
            'id': db_user.user_id,
            'name': db_user.get_full_name() or db_user.username,
            'email': db_user.email,
            'phone': db_user.phone,
            'country': db_user.country,
            'registration_date': db_user.date_joined.strftime('%d.%m.%Y'),
            'personal_volume': float(lo_amount),  # Из API
            'group_volume': float(db_user.group_volume),
            'partner_level': db_user.partner_level,
            'user_type': db_user.user_type,
            'total_referrals': db_user.total_referrals,
            'active_referrals': db_user.active_referrals,
            'earnings': float(db_user.earnings),
            'available_for_withdrawal': float(db_user.available_for_withdrawal),
            'middle_name': db_user.middle_name or '',
            'passport_number': db_user.passport_number or '',
            'is_email_verified': db_user.is_email_verified,
            'is_terms_accepted': db_user.is_terms_accepted,
            'referral_code': db_user.referral_code,
            'error': False
        }
        
        return JsonResponse(data)
        
    except CustomUser.DoesNotExist:
        return JsonResponse({'error': True, 'message': 'Пользователь не найден'}, status=404)
    except Exception as e:
        logger.error(f"Ошибка при получении деталей реферала: {e}")
        return JsonResponse({'error': True, 'message': str(e)}, status=500)






######################################################################################

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash

from .forms import ProfileUpdateForm, CustomSetPasswordForm


@login_required
def settings_view(request):
    user = request.user

    if request.method == 'POST':
        profile_form = ProfileUpdateForm(request.POST, instance=user)
        password_form = CustomSetPasswordForm(user, request.POST)

        if 'update_profile' in request.POST:
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Профиль обновлен')
                return redirect('cabinet:settings')

        elif 'change_password' in request.POST:
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Пароль успешно изменён')
                return redirect('cabinet:settings')

    else:
        profile_form = ProfileUpdateForm(instance=user)
        password_form = CustomSetPasswordForm(user)

    return render(request, 'cabinet/settings.html', {
        'profile_form': profile_form,
        'password_form': password_form,
    })
