# cabinet/urls.py
from django.urls import path
from . import views

app_name = 'cabinet'  # Добавьте это

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('purchases/', views.purchases_view, name='purchases'),
    path('finance/', views.finance_view, name='finance'),
    path('api/refresh-stats/', views.refresh_stats, name='refresh_stats'),
    path('api/get-stats/', views.get_stats_json, name='get_stats_json'),
]
