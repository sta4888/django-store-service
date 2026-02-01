from django.contrib import admin
from mptt.admin import MPTTModelAdmin, DraggableMPTTAdmin
from .models import Category, Product, Attribute, AttributeValue


# Вариант 1: Простой MPTT админ
@admin.register(Category)
class CategoryAdmin(MPTTModelAdmin):
    list_display = ('name', 'slug', 'parent', 'is_active', 'created_at', 'is_root_property')
    list_display_links = ('name',)
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')

    # Удаляем list_filter для is_root, так как это свойство, а не поле

    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'parent', 'description', 'is_active')
        }),
        ('Дополнительно', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def is_root_property(self, obj):
        """Отображение свойства is_root в админке"""
        return obj.is_root

    is_root_property.short_description = 'Корневая?'
    is_root_property.boolean = True


# ИЛИ Вариант 2: DraggableMPTTAdmin (с возможностью перетаскивания)
# @admin.register(Category)
# class CategoryAdmin(DraggableMPTTAdmin):
#     list_display = ('tree_actions', 'indented_title', 'slug', 'is_active', 'product_count')
#     list_display_links = ('indented_title', 'slug')
#     list_filter = ('is_active',)
#     search_fields = ('name', 'slug', 'description')
#     prepopulated_fields = {'slug': ('name',)}

#     def get_queryset(self, request):
#         return super().get_queryset(request).prefetch_related('products')

#     def product_count(self, obj):
#         return obj.products.count()
#     product_count.short_description = 'Товаров'

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'in_stock', 'quantity', 'is_active', 'created_at')
    list_filter = ('is_active', 'in_stock', 'category', 'created_at')
    search_fields = ('name', 'sku', 'description', 'short_description')
    list_editable = ('price', 'quantity', 'is_active')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('attributes',)

    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'slug', 'category', 'sku', 'description', 'short_description')
        }),
        ('Цена и наличие', {
            'fields': ('price', 'old_price', 'quantity', 'in_stock')
        }),
        ('Атрибуты', {
            'fields': ('attributes',)
        }),
        ('Дополнительно', {
            'fields': ('is_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'filter_type', 'unit', 'order')
    list_editable = ('order',)
    search_fields = ('name', 'code')
    prepopulated_fields = {'code': ('name',)}


@admin.register(AttributeValue)
class AttributeValueAdmin(admin.ModelAdmin):
    list_display = ('attribute', 'value', 'code', 'order', 'product_count')
    list_filter = ('attribute',)
    list_editable = ('order',)
    search_fields = ('value', 'code')

    def product_count(self, obj):
        return obj.products.count()

    product_count.short_description = 'Используется в товарах'