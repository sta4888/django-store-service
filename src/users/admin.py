from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Админка для кастомного пользователя"""

    list_display = ('internal_id', 'username', 'email', 'referral_code',
                    'is_external', 'is_partner', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active',
                   'is_external', 'is_partner')
    search_fields = ('internal_id', 'username', 'email', 'referral_code')
    readonly_fields = ('internal_id', 'referral_code', 'created_at')
    ordering = ('internal_id',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Internal info', {
            'fields': ('internal_id', 'referral_code', 'referrer',
                       'is_external', 'is_partner', 'created_at'),
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser',
                       'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2',
                       'is_external', 'is_partner'),
        }),
    )
