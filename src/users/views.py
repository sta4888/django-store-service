from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash, logout, authenticate, login
from django.core.paginator import Paginator
from django.db.models import Sum, Count
from .forms import LoginForm, CustomUserCreationForm, PasswordChangeForm, UserUpdateForm, ProfileUpdateForm
from .models import UserProfile, User



@login_required
def profile(request):
    """Личный кабинет - главная страница с MLM статистикой"""
    user = request.user
    profile = user.profile

    # Получаем последние заказы пользователя
    # recent_orders = Order.objects.filter(user=user).order_by('-created_at')[:5]

    # Заглушки для новостей (позже заменить на реальную модель)
    recent_news = [
        {'title': 'Новая линейка продуктов', 'excerpt': 'Представляем новую линейку органических БАДов',
         'created_at': '18.02.2024'},
        {'title': 'Повышение бонусов', 'excerpt': 'С марта увеличиваем бонусные выплаты', 'created_at': '15.02.2024'},
        {'title': 'Обновление личного кабинета', 'excerpt': 'Мы обновили интерфейс личного кабинета',
         'created_at': '10.02.2024'},
    ]

    context = {
        'user': user,
        'profile': profile,
        # 'recent_orders': recent_orders,
        'recent_news': recent_news,
        'active_tab': 'overview',
    }
    return render(request, 'users/profile.html', context)


@login_required
def profile_edit(request):
    """Редактирование профиля"""
    user = request.user
    profile = user.profile

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Профиль успешно обновлен')
            return redirect('users:profile')
    else:
        user_form = UserUpdateForm(instance=user)
        profile_form = ProfileUpdateForm(instance=profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'active_tab': 'edit',
    }
    return render(request, 'users/profile_edit.html', context)


@login_required
def password_change(request):
    """Смена пароля"""
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, request.user)  # Обновляем сессию
            messages.success(request, 'Пароль успешно изменен')
            return redirect('users:profile')
    else:
        form = PasswordChangeForm(user=request.user)

    context = {
        'form': form,
        'active_tab': 'password',
    }
    return render(request, 'users/password_change.html', context)


@login_required
def referral_system(request):
    """Реферальная система"""
    user = request.user
    referred_users = user.referred_users.all().select_related('profile')

    # Статистика по рефералам
    referral_stats = {
        'total_referred': referred_users.count(),
        'active_referred': referred_users.filter(is_active=True).count(),
        'recent_referred': referred_users.order_by('-date_joined')[:10],
        'total_volume': referred_users.aggregate(
            total=Sum('profile__personal_volume')
        )['total'] or 0,
    }

    context = {
        'user': user,
        'referred_users': referred_users,
        'referral_stats': referral_stats,
        'referral_link': request.build_absolute_uri(f'/?ref={user.referral_code}'),
        'active_tab': 'referrals',
    }
    return render(request, 'users/referral_system.html', context)


@login_required
def structure(request):
    """Моя MLM структура"""
    user = request.user

    # Получаем партнеров разных уровней (упрощенно)
    level1_partners = user.referred_users.all()
    level2_partners = User.objects.filter(referred_by__in=level1_partners)
    level3_partners = User.objects.filter(referred_by__in=level2_partners)

    # Статистика структуры
    structure_stats = {
        'level1_count': level1_partners.count(),
        'level2_count': level2_partners.count(),
        'level3_count': level3_partners.count(),
        'total_partners': level1_partners.count() + level2_partners.count() + level3_partners.count(),
        'active_partners': level1_partners.filter(is_active=True).count(),
    }

    context = {
        'user': user,
        'level1_partners': level1_partners,
        'structure_stats': structure_stats,
        'active_tab': 'structure',
    }
    return render(request, 'users/structure.html', context)


# @login_required
# def orders(request):
#     """История заказов"""
#     user = request.user
#     # orders_list = Order.objects.filter(user=user).order_by('-created_at')
#
#     # Пагинация
#     paginator = Paginator(orders_list, 10)
#     page = request.GET.get('page')
#     orders_page = paginator.get_page(page)
#
#     context = {
#         'user': user,
#         'orders': orders_page,
#         'active_tab': 'orders',
#     }
#     return render(request, 'users/orders.html', context)
#

@login_required
def finance(request):
    """Финансы и начисления"""
    user = request.user
    profile = user.profile

    # Заглушки для истории начислений (позже заменить на модель)
    earnings_history = [
        {'date': '15.02.2024', 'type': 'Личный бонус', 'amount': 23500, 'status': 'paid'},
        {'date': '10.02.2024', 'type': 'Групповой бонус', 'amount': 42800, 'status': 'paid'},
        {'date': '05.02.2024', 'type': 'Бонус лидера', 'amount': 12150, 'status': 'pending'},
        {'date': '28.01.2024', 'type': 'Личный бонус', 'amount': 18900, 'status': 'paid'},
    ]

    context = {
        'user': user,
        'profile': profile,
        'earnings_history': earnings_history,
        'active_tab': 'finance',
    }
    return render(request, 'users/finance.html', context)


@login_required
def register_partner(request):
    """Регистрация нового партнера"""
    from django.contrib.auth.forms import UserCreationForm

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.referred_by = request.user
            new_user.save()

            messages.success(request, f'Партнер {new_user.username} успешно зарегистрирован в вашей структуре')
            return redirect('users:structure')
    else:
        form = UserCreationForm()

    context = {
        'form': form,
        'active_tab': 'register_partner',
    }
    return render(request, 'users/register_partner.html', context)


def register(request):
    """Регистрация нового пользователя"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Автоматический вход после регистрации
            login(request, user)

            # Сообщение об успешной регистрации
            messages.success(request, f'Добро пожаловать, {user.username}! Ваш аккаунт успешно создан.')

            # Перенаправление на страницу профиля
            return redirect('users:profile')
    else:
        # Обработка реферального кода из GET-параметра
        initial = {}
        referral_code = request.GET.get('ref')
        if referral_code:
            initial['referral_code'] = referral_code
        form = CustomUserCreationForm(initial=initial)

    context = {
        'form': form,
        'title': 'Регистрация',
    }
    return render(request, 'users/register.html', context)


def custom_login(request):
    """Кастомный вход в систему"""
    if request.user.is_authenticated:
        return redirect('users:profile')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            remember_me = form.cleaned_data.get('remember_me', False)

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)

                # Настройка сессии для "запомнить меня"
                if not remember_me:
                    request.session.set_expiry(0)

                messages.success(request, f'Добро пожаловать, {user.username}!')

                # Перенаправление на следующую страницу или профиль
                next_url = request.GET.get('next', 'users:profile')
                return redirect(next_url)
            else:
                messages.error(request, 'Неверное имя пользователя или пароль')
    else:
        form = LoginForm()

    context = {
        'form': form,
        'title': 'Вход в систему',
    }
    return render(request, 'users/login.html', context)


def custom_logout(request):
    """Выход из системы"""
    logout(request)
    messages.info(request, 'Вы успешно вышли из системы')
    return redirect('catalog:index')