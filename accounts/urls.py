from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Авторизация
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('verify-email/', views.verify_email_view, name='verify_email'),
    path('resend-code/', views.resend_verification_code_view, name='resend_code'),
    path('generate-new-link/', views.generate_new_referral_link, name='generate_new_link'),

    # Мониторинг Celery (только для staff)
    path('celery/tasks/', views.task_results_view, name='task_results'),
    path('celery/tasks/<str:task_id>/', views.task_result_detail_view, name='task_result_detail'),
]