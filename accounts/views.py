import json
import logging

from django.db.models import Count
from django.contrib.auth.decorators import login_required, user_passes_test
from django_celery_results.models import TaskResult
from django.db.models import Count, Q
from datetime import datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.http import Http404

from cabinet.services.fastapi_service import FastAPIService
from .models import CustomUser
from .forms import ReferralRegistrationForm, EmailVerificationForm, LoginForm
from .tasks import send_verification_email_task, send_welcome_email_task, send_referral_notification_task

logger = logging.getLogger(__name__)

def referral_register_view(request, referral_link):
    """Регистрация по реферальной ссылке"""
    try:
        referrer = CustomUser.objects.get(referral_link=referral_link)
    except CustomUser.DoesNotExist:
        messages.error(request, 'Неверная реферальная ссылка')
        return redirect('accounts:login')

    if request.method == 'POST':
        form = ReferralRegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(referrer=referrer)

                # Генерация кода подтверждения
                verification_code = user.generate_email_verification_code()

                # Отправка email через Celery (асинхронно)
                send_verification_email_task.delay(
                    email=user.email,
                    code=verification_code,
                    username=user.get_full_name()
                )

                # Сохраняем user_id в сессии для подтверждения email
                request.session['user_for_verification'] = user.user_id
                request.session['email_for_verification'] = user.email

                messages.success(request,
                                 f'Регистрация успешна! На почту {user.email} отправлен код подтверждения.')
                return redirect('accounts:verify_email')

            except Exception as e:
                messages.error(request, f'Ошибка при регистрации: {str(e)}')
    else:
        form = ReferralRegistrationForm()

    context = {
        'form': form,
        'referrer': referrer,
        'referral_link': referral_link
    }
    return render(request, 'accounts/referral_register.html', context)


def verify_email_view(request):
    """Подтверждение email"""
    user_id = request.session.get('user_for_verification')
    email = request.session.get('email_for_verification')

    if not user_id or not email:
        messages.error(request, 'Сессия истекла. Пожалуйста, зарегистрируйтесь снова.')
        return redirect('accounts:login')

    try:
        user = CustomUser.objects.get(user_id=user_id, email=email)
    except CustomUser.DoesNotExist:
        messages.error(request, 'Пользователь не найден')
        return redirect('accounts:login')

    if request.method == 'POST':
        form = EmailVerificationForm(request.POST, user=user)
        if form.is_valid():
            # Подтверждаем email
            user.is_email_verified = True
            user.email_verification_code = None
            user.email_verification_sent_at = None
            user.save()

            service = FastAPIService()
            referrer_id = user.referrer.username if user.referrer else None
            data = service.add_user(user_id=user.username, referrer_id=referrer_id)
            logger.info(f"FastAPI add new user {user.username} with referrer {referrer_id}")

            # Автоматический вход
            login(request, user)
            # Отправляем приветственное письмо через Celery
            send_welcome_email_task.delay(user.user_id)

            # Отправляем уведомление рефереру через Celery
            if user.referrer:
                send_referral_notification_task.delay(user.referrer.user_id, user.user_id)

            # Очищаем сессию
            request.session.pop('user_for_verification', None)
            request.session.pop('email_for_verification', None)

            messages.success(request,
                             f'Email успешно подтвержден! Добро пожаловать, {user.get_full_name()}! '
                             f'Ваш ID для входа: {user.user_id}')
            return redirect('cabinet:dashboard')
    else:
        form = EmailVerificationForm(user=user)

    # Отправляем новый код если срок истек
    if user.is_verification_code_expired():
        new_code = user.generate_email_verification_code()
        send_verification_email_task.delay(
            email=user.email,
            code=new_code,
            username=user.get_full_name()
        )
        messages.info(request, 'Новый код подтверждения отправлен на вашу почту.')

    context = {
        'form': form,
        'email': email,
        'user': user
    }
    return render(request, 'accounts/verify_email.html', context)


def resend_verification_code_view(request):
    """Повторная отправка кода подтверждения"""
    user_id = request.session.get('user_for_verification')
    email = request.session.get('email_for_verification')

    if not user_id or not email:
        messages.error(request, 'Сессия истекла')
        return redirect('accounts:login')

    try:
        user = CustomUser.objects.get(user_id=user_id, email=email)
    except CustomUser.DoesNotExist:
        messages.error(request, 'Пользователь не найден')
        return redirect('accounts:login')

    # Генерация нового кода
    new_code = user.generate_email_verification_code()

    # Отправка через Celery
    send_verification_email_task.delay(
        email=user.email,
        code=new_code,
        username=user.get_full_name()
    )

    messages.success(request, 'Новый код подтверждения отправлен на вашу почту.')
    return redirect('accounts:verify_email')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('cabinet:dashboard')

    if request.method == 'POST':
        # Получаем данные из формы
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        print(f"DEBUG: Попытка входа - username: '{username}'")  # Отладка

        # Сначала пробуем найти пользователя по user_id
        user = None
        login_method = None

        try:
            # 1. Поиск по user_id
            user_obj = CustomUser.objects.get(user_id=username)
            user = authenticate(request, username=user_obj.username, password=password)
            login_method = 'by user_id'
        except CustomUser.DoesNotExist:
            pass

        if not user:
            try:
                # 2. Поиск по email
                user_obj = CustomUser.objects.get(email=username)
                user = authenticate(request, username=user_obj.username, password=password)
                login_method = 'by email'
            except CustomUser.DoesNotExist:
                pass

        if not user:
            # 3. Прямой поиск по username
            user = authenticate(request, username=username, password=password)
            if user:
                login_method = 'by username'

        print(f"DEBUG: Найден пользователь: {user}, метод: {login_method}")  # Отладка

        if user is not None:
            # ВРЕМЕННО отключаем проверку верификации email
            # if not user.is_email_verified:
            #     messages.error(request, 'Email не подтвержден. Проверьте вашу почту.')
            #     return redirect('accounts:login')

            if not user.is_active:
                messages.error(request, 'Аккаунт деактивирован.')
                return redirect('accounts:login')

            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.get_full_name() or user.user_id}!')
            return redirect('cabinet:dashboard')
        else:
            messages.error(request, 'Неверные учетные данные')
            print(f"DEBUG: Аутентификация не удалась")  # Отладка

    return render(request, 'accounts/login.html')

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы.')
    return redirect('accounts:login')


@login_required
def generate_new_referral_link(request):
    """Генерация новой реферальной ссылки"""
    user = request.user

    # Генерируем новый уникальный код
    import uuid
    new_code = uuid.uuid4().hex[:16].upper()

    # Проверяем уникальность
    while CustomUser.objects.filter(referral_link=f"ref-{new_code}").exists():
        new_code = uuid.uuid4().hex[:16].upper()

    user.referral_code = new_code
    user.referral_link = f"ref-{new_code}"
    user.save()

    messages.success(request, 'Новая реферальная ссылка успешно сгенерирована!')
    return redirect('cabinet:dashboard')


# Вспомогательная функция для отправки email
def send_verification_email(to_email, code, username):
    subject = 'Код подтверждения email - EVERON'
    message = f'''
    Здравствуйте, {username}!

    Ваш код подтверждения email: {code}

    Введите этот код на странице подтверждения для завершения регистрации.

    Код действителен в течение 15 минут.

    С уважением,
    Команда EVERON
    '''

    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [to_email]

    try:
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        return True
    except Exception as e:
        print(f"Ошибка отправки email: {e}")
        return False

def registration_info_view(request):
    """Страница с информацией о регистрации"""
    return render(request, 'accounts/registration_info.html')


def is_staff_or_superuser(user):
    return user.is_staff or user.is_superuser


@login_required
@user_passes_test(is_staff_or_superuser)
def task_results_view(request):
    """Просмотр результатов задач Celery"""

    # Фильтрация
    task_name = request.GET.get('task_name', '')
    status = request.GET.get('status', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    tasks = TaskResult.objects.all()

    if task_name:
        tasks = tasks.filter(task_name__icontains=task_name)

    if status:
        tasks = tasks.filter(status=status)

    if date_from:
        try:
            date_from_obj = timezone.datetime.strptime(date_from, '%Y-%m-%d')
            tasks = tasks.filter(date_done__gte=date_from_obj)
        except ValueError:
            pass

    if date_to:
        try:
            date_to_obj = timezone.datetime.strptime(date_to, '%Y-%m-%d')
            tasks = tasks.filter(date_done__lte=date_to_obj)
        except ValueError:
            pass

    # Статистика
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)

    stats = {
        'total': TaskResult.objects.count(),
        'success': TaskResult.objects.filter(status='SUCCESS').count(),
        'failure': TaskResult.objects.filter(status='FAILURE').count(),
        'today': TaskResult.objects.filter(date_done__date=today).count(),
        'last_7_days': TaskResult.objects.filter(date_done__date__gte=week_ago).count(),
    }

    # Популярные задачи
    popular_tasks = TaskResult.objects.values('task_name').annotate(
        count=Count('id'),
        success=Count('id', filter=Q(status='SUCCESS')),
        failure=Count('id', filter=Q(status='FAILURE'))
    ).order_by('-count')[:10]

    context = {
        'tasks': tasks.order_by('-date_done')[:100],
        'stats': stats,
        'popular_tasks': popular_tasks,
        'task_name': task_name,
        'status': status,
        'date_from': date_from,
        'date_to': date_to,
        'status_choices': ['SUCCESS', 'FAILURE', 'PENDING', 'STARTED', 'RETRY'],
    }

    return render(request, 'accounts/task_results.html', context)


@login_required
@user_passes_test(is_staff_or_superuser)
def task_result_detail_view(request, task_id):
    """Детальная информация о задаче"""
    try:
        task = TaskResult.objects.get(task_id=task_id)

        # Пытаемся парсить результат как JSON
        try:
            result_data = json.loads(task.result) if task.result else {}
        except:
            result_data = {'raw_result': task.result}

        context = {
            'task': task,
            'result_data': result_data,
        }

        return render(request, 'accounts/task_result_detail.html', context)
    except TaskResult.DoesNotExist:
        messages.error(request, 'Задача не найдена')
        return redirect('accounts:task_results')


def forgot_password(request):
    if request.method == "POST":
        form = ForgotPasswordForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data["email"]
            user = CustomUser.objects.get(email__iexact=email)

            code = user.generate_email_verification_code()

            send_verification_email_task.delay(
                email=user.email,
                code=code,
                username=user.get_full_name()
            )

            request.session["user_for_verification"] = user.user_id
            request.session["email_for_verification"] = user.email
            request.session["password_reset"] = True

            messages.info(request, "Код подтверждения отправлен на вашу почту.")
            return redirect("accounts:verify_email")
    else:
        form = ForgotPasswordForm()

    return render(request, "accounts/forgot_password.html", {"form": form})