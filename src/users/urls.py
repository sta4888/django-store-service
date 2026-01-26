from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # Профиль
    path('', views.profile, name='profile'),
    path('edit/', views.profile_edit, name='profile_edit'),
    path('password/', views.password_change, name='password_change'),
    path('referrals/', views.referral_system, name='referral_system'),
    path('structure/', views.structure, name='structure'),
    # path('profile/orders/', views.orders, name='orders'),
    path('finance/', views.finance, name='finance'),
    path('register-partner/', views.register_partner, name='register_partner'),

    # Аутентификация
    path('register/', views.register, name='register'),
    path('login/', views.custom_login, name='login'),
    path('logout/', views.custom_logout, name='logout'),
]