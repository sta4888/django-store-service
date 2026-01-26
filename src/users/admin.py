from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, UserProfile
from .forms import CustomUserCreationForm, UserUpdateForm


class CustomUserAdmin(UserAdmin):
    """Кастомная админка для пользователей"""

    add_form = CustomUserCreationForm
    form = UserUpdateForm
    model = User

    list_display = ('username', 'email', 'first_name', 'last_name',
                    'is_staff', 'is_active', 'date_joined', 'referral_code')

    list_filter = ('is_staff', 'is_active', 'is_superuser',
                   'is_external', 'date_joined')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('MLM info'), {'fields': ('referral_code', 'referred_by', 'is_external')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name',
                       'password1', 'password2', 'is_staff', 'is_active',
                       'referral_code', 'referred_by'),
        }),
    )

    search_fields = ('username', 'email', 'first_name', 'last_name', 'referral_code')
    ordering = ('-date_joined',)
    readonly_fields = ('last_login', 'date_joined', 'referral_code')
    filter_horizontal = ('groups', 'user_permissions',)


class UserProfileAdmin(admin.ModelAdmin):
    """Админка для профилей пользователей"""

    list_display = ('user', 'phone', 'level', 'personal_volume',
                    'group_volume', 'earnings', 'total_orders')

    list_filter = ('level', 'email_notifications', 'sms_notifications',
                   'created_at')

    fieldsets = (
        (_('User info'), {'fields': ('user',)}),
        (_('Personal info'), {'fields': ('phone', 'avatar', 'birth_date')}),
        (_('Address'), {'fields': ('address', 'city', 'postal_code')}),
        (_('MLM Statistics'), {'fields': ('level', 'personal_volume',
                                          'group_volume', 'earnings',
                                          'available_for_withdrawal',
                                          'active_partners')}),
        (_('Bonuses'), {'fields': ('personal_bonus', 'group_bonus',
                                   'leader_bonus')}),
        (_('Growth'), {'fields': ('personal_volume_growth',
                                  'group_volume_growth',
                                  'earnings_growth',
                                  'level_progress')}),
        (_('Notifications'), {'fields': ('email_notifications',
                                         'sms_notifications')}),
        (_('Purchase Statistics'), {'fields': ('total_orders',
                                               'total_spent')}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at')}),
    )

    readonly_fields = ('created_at', 'updated_at')
    search_fields = ('user__username', 'user__email', 'phone', 'city')
    ordering = ('-created_at',)

    def get_queryset(self, request):
        """Оптимизация запросов"""
        return super().get_queryset(request).select_related('user')


# Регистрация моделей в админке
admin.site.register(User, CustomUserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)