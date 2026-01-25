from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, Attribute, AttributeValue


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Админка для категорий"""

    list_display = ('name', 'slug', 'parent', 'is_active', 'is_root', 'product_count')
    list_filter = ('is_active', 'is_root')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

    def product_count(self, obj):
        return obj.products.count()

    product_count.short_description = 'Количество товаров'


class AttributeValueInline(admin.TabularInline):
    """Inline для значений атрибута"""
    model = AttributeValue
    extra = 1


@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    """Админка для атрибутов"""

    list_display = ('name', 'code', 'filter_type', 'unit', 'order')
    list_filter = ('filter_type',)
    search_fields = ('name', 'code')
    inlines = [AttributeValueInline]
    prepopulated_fields = {'code': ('name',)}


@admin.register(AttributeValue)
class AttributeValueAdmin(admin.ModelAdmin):
    """Админка для значений атрибутов"""

    list_display = ('attribute', 'value', 'code', 'order', 'product_count')
    list_filter = ('attribute',)
    search_fields = ('value', 'code')

    def product_count(self, obj):
        return obj.products.count()

    product_count.short_description = 'Количество товаров'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Админка для товаров"""

    list_display = ('name', 'sku', 'category', 'price', 'old_price',
                    'in_stock', 'quantity', 'is_active', 'created_at')
    list_filter = ('is_active', 'in_stock', 'category', 'created_at')
    search_fields = ('name', 'sku', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at', 'display_discount')
    filter_horizontal = ('attributes',)  # ← вместо inline для ManyToMany
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'sku', 'category', 'is_active')
        }),
        ('Цены и наличие', {
            'fields': ('price', 'old_price', 'quantity', 'in_stock')
        }),
        ('Описания', {
            'fields': ('short_description', 'description')
        }),
        ('Атрибуты', {
            'fields': ('attributes',),
            'classes': ('collapse',)
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at', 'display_discount'),
            'classes': ('collapse',)
        }),
    )

    def display_discount(self, obj):
        if obj.has_discount:
            return format_html(
                '<span style="color: green; font-weight: bold;">{}%</span>',
                obj.discount_percent
            )
        return '—'

    display_discount.short_description = 'Скидка'