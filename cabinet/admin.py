from django.contrib import admin

from .models import MonthlyReport, News, Purchase


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('user', 'order_number', 'product_name', 'amount', 'status', 'date')
    list_filter = ('status', 'date')
    search_fields = ('user__username', 'order_number', 'product_name')


@admin.register(MonthlyReport)
class MonthlyReportAdmin(admin.ModelAdmin):
    list_display = ('user', 'year', 'month', 'personal_volume', 'group_volume', 'side_volume', 'points', 'veron', 'bonus_total', 'total_income', 'partner_level', 'created_at')
    list_filter = ('year', 'month', 'partner_level')
    search_fields = ('user__username',)
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Период', {
            'fields': ('user', 'year', 'month', 'partner_level')
        }),
        ('Объёмы', {
            'fields': ('personal_volume', 'group_volume', 'side_volume')
        }),
        ('Баллы и вероны', {
            'fields': ('points', 'veron')
        }),
        ('Бонусы', {
            'fields': ('personal_bonus', 'structure_bonus', 'mentor_bonus', 'extra_bonus', 'bonus_total')
        }),
        ('Доход', {
            'fields': ('personal_money', 'group_money', 'leader_money', 'side_vol_money', 'total_money', 'total_income')
        }),
        ('Рефералы', {
            'fields': ('new_referrals', 'active_referrals_count')
        }),
        ('Покупки', {
            'fields': ('purchases_count', 'purchases_amount')
        }),
        ('Служебное', {
            'fields': ('created_at',)
        }),
    )


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'is_published')
    list_filter = ('is_published',)
