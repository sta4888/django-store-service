from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # Поля для отображения в списке
    list_display = ('username', 'email', 'first_name', 'last_name',
                    'is_email_verified', 'is_staff', 'is_active')
    list_filter = ('is_email_verified', 'is_staff', 'is_superuser', 'is_active', 'partner_level')
    search_fields = ('user_id', 'username', 'email', 'first_name', 'last_name', 'phone')

    # Порядок полей в форме редактирования
    fieldsets = (
        (None, {'fields': ('user_id', 'username', 'password')}),
        ('Персональная информация', {'fields': ('first_name', 'last_name', 'middle_name',
                                                'email', 'phone', 'country', 'passport_number')}),
        ('Реферальная информация', {'fields': ('referral_code', 'referral_link', 'referrer')}),
        ('Верификация', {'fields': ('is_email_verified', 'email_verification_code',
                                    'email_verification_sent_at', 'is_terms_accepted')}),
        ('Статистика', {'fields': ('personal_volume', 'group_volume', 'earnings',
                                   'available_for_withdrawal', 'partner_level',
                                   'total_referrals', 'active_referrals')}),
        ('Разрешения', {'fields': ('is_active', 'is_staff', 'is_superuser',
                                   'groups', 'user_permissions')}),
        ('Важные даты', {'fields': ('last_login', 'date_joined', 'registration_date')}),
    )

    # Поля только для чтения
    readonly_fields = ('user_id', 'referral_code', 'referral_link', 'date_joined',
                       'registration_date', 'email_verification_sent_at')

    # Поля при создании пользователя
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2',
                       'first_name', 'last_name', 'middle_name',
                       'phone', 'country', 'passport_number',
                       'is_email_verified', 'is_terms_accepted',
                       'is_staff', 'is_superuser', 'is_active'),
        }),
    )

    # Порядок сортировки
    ordering = ('user_id',)