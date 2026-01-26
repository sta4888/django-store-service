
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # Подключаем URLs каталога
    path('', include('catalog.urls', namespace='catalog')),
    path('users/', include('users.urls', namespace='users')),
]
