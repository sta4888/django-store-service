from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from accounts import views as accounts_views

urlpatterns = [
    path('', include('catalog.urls', namespace='catalog')),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('cabinet/', include('cabinet.urls')),
    path('register/<str:referral_link>/', accounts_views.referral_register_view, name='referral_register'),
    path('login/', RedirectView.as_view(pattern_name='accounts:login', permanent=False)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
