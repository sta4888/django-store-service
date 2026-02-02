from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from datetime import timedelta
from django_celery_results.models import TaskResult


@shared_task(bind=True)
def send_verification_email_task(self, email, code, username):
    """
    Отправка email с кодом подтверждения через Celery
    """
    subject = 'Код подтверждения email - EVERON'

    html_message = render_to_string('accounts/email/verification_email.html', {
        'username': username,
        'code': code,
        'support_email': settings.DEFAULT_FROM_EMAIL,
    })

    plain_message = strip_tags(html_message)

    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            html_message=html_message,
            fail_silently=False,
        )

        return {
            'status': 'success',
            'email': email,
            'message': f'Код подтверждения отправлен на {email}',
        }
    except Exception as e:
        # Подробное логирование
        error_msg = f"Ошибка отправки email на {email}: {str(e)}"
        print(error_msg)

        # Можно также логировать в файл или Sentry
        import logging
        logger = logging.getLogger(__name__)
        logger.error(error_msg)

        # Повторная попытка через 5 минут при ошибке
        self.retry(exc=e, countdown=300, max_retries=3)

        return {
            'status': 'error',
            'email': email,
            'error': str(e),
        }


@shared_task
def send_welcome_email_task(user_id):
    """
    Отправка приветственного письма после регистрации
    """
    from .models import CustomUser

    try:
        user = CustomUser.objects.get(user_id=user_id)

        subject = 'Добро пожаловать в EVERON!'

        html_message = render_to_string('accounts/email/welcome_email.html', {
            'user': user,
            'support_email': settings.DEFAULT_FROM_EMAIL,
        })

        plain_message = strip_tags(html_message)

        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )

        return {'status': 'success', 'user_id': user_id}
    except CustomUser.DoesNotExist:
        return {'status': 'error', 'message': 'Пользователь не найден'}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}


@shared_task
def send_password_reset_email_task(email, reset_link):
    """
    Отправка письма для сброса пароля
    """
    subject = 'Сброс пароля - EVERON'

    html_message = render_to_string('accounts/email/password_reset.html', {
        'reset_link': reset_link,
        'support_email': settings.DEFAULT_FROM_EMAIL,
    })

    plain_message = strip_tags(html_message)

    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        html_message=html_message,
        fail_silently=False,
    )

    return {'status': 'success', 'email': email}


@shared_task
def send_referral_notification_task(referrer_id, new_user_id):
    """
    Уведомление реферера о новом регистрации
    """
    from .models import CustomUser

    try:
        referrer = CustomUser.objects.get(user_id=referrer_id)
        new_user = CustomUser.objects.get(user_id=new_user_id)

        subject = 'Новый партнер в вашей структуре!'

        html_message = render_to_string('accounts/email/referral_notification.html', {
            'referrer': referrer,
            'new_user': new_user,
            'support_email': settings.DEFAULT_FROM_EMAIL,
        })

        plain_message = strip_tags(html_message)

        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[referrer.email],
            html_message=html_message,
            fail_silently=False,
        )

        return {'status': 'success', 'referrer_id': referrer_id, 'new_user_id': new_user_id}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

#
# @shared_task
# def cleanup_old_task_results():
#     """
#     Очистка старых результатов задач (старше 7 дней)
#     """
#     week_ago = timezone.now() - timedelta(days=7)
#     deleted_count, _ = TaskResult.objects.filter(date_done__lt=week_ago).delete()
#
#     return {
#         'status': 'success',
#         'message': f'Удалено {deleted_count} старых результатов задач',
#         'timestamp': timezone.now().isoformat(),
#     }
#
#
# @shared_task
# def send_daily_stats():
#     """
#     Отправка ежедневной статистики администраторам
#     """
#     from .models import CustomUser
#     from django.contrib.auth.models import User
#
#     # Получаем статистику
#     total_users = CustomUser.objects.count()
#     new_users_today = CustomUser.objects.filter(
#         date_joined__date=timezone.now().date()
#     ).count()
#     verified_users = CustomUser.objects.filter(is_email_verified=True).count()
#
#     # Получаем администраторов
#     admins = User.objects.filter(is_staff=True, is_active=True)
#     admin_emails = [admin.email for admin in admins if admin.email]
#
#     if not admin_emails:
#         return {'status': 'error', 'message': 'Нет email администраторов'}
#
#     subject = f'Ежедневная статистика EVERON - {timezone.now().strftime("%d.%m.%Y")}'
#
#     html_message = render_to_string('accounts/email/daily_stats.html', {
#         'date': timezone.now().strftime("%d.%m.%Y"),
#         'total_users': total_users,
#         'new_users_today': new_users_today,
#         'verified_users': verified_users,
#         'verification_rate': (verified_users / total_users * 100) if total_users > 0 else 0,
#     })
#
#     plain_message = strip_tags(html_message)
#
#     try:
#         send_mail(
#             subject=subject,
#             message=plain_message,
#             from_email=settings.DEFAULT_FROM_EMAIL,
#             recipient_list=admin_emails,
#             html_message=html_message,
#             fail_silently=False,
#         )
#
#         return {
#             'status': 'success',
#             'message': f'Статистика отправлена {len(admin_emails)} администраторам',
#             'timestamp': timezone.now().isoformat(),
#         }
#     except Exception as e:
#         return {
#             'status': 'error',
#             'error': str(e),
#             'timestamp': timezone.now().isoformat(),
#         }
#
#
# @shared_task
# def test_celery_connection():
#     """
#     Тестовая задача для проверки работы Celery
#     """
#     return {
#         'status': 'success',
#         'message': 'Celery работает корректно!',
#         'timestamp': timezone.now().isoformat(),
#         'django_settings': settings.DEBUG,
#     }
