# cabinet/urls.py
from django.urls import path
from . import views

app_name = 'cabinet'  # Добавьте это

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('purchases/', views.purchases_view, name='purchases'),
    path('finance/', views.finance_view, name='finance'),
    path('structure/', views.structure_view, name='structure'),
    path('settings/', views.settings_view, name='settings'),
    

    path('api/user/status/', views.get_user_data, name='get_user_data'),
    path('api/user/team/', views.get_user_team, name='get_user_team'),
    path('api/user/lo/add/', views.add_user_lo, name='add_user_lo'),
    path('api/user/lo/subtract/', views.sub_user_lo, name='sub_user_lo'),
    path('api/referrals/', views.get_referrals_json, name='referrals_json'),
    path('api/referrals/<str:user_id>/details/', views.get_referral_details, name='referral_details'),

    path('admin/', views.admin_panel, name='admin_page'),

]
