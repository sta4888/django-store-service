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
    # path('api/get-data/', views.get_user_data, name='get_data_json'),
    # path('api/add-lo/', views.add_user_lo, name='add_user_lo'),
    # path('api/sub-lo/', views.sub_user_lo, name='sub_user_lo'),
    # path('api/get-team/', views.get_user_team, name='get_user_team'),

    path('api/user/status/', views.get_user_data, name='get_user_data'),
    path('api/user/team/', views.get_user_team, name='get_user_team'),
    path('api/user/lo/add/', views.add_user_lo, name='add_user_lo'),
    path('api/user/lo/subtract/', views.sub_user_lo, name='sub_user_lo'),

    path('admin/api-test/', views.api_test_page, name='api_test_page'),

]
