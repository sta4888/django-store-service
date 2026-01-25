from django.urls import path
from . import views

app_name = 'catalog'  # ← это создаст namespace 'catalog'

urlpatterns = [
    # Главная страница каталога
    path('', views.index, name='index'),

    # Страница категории
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),

    # Страница товара
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
]