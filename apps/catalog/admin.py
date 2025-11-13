from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from django.urls import reverse
from .models import Category, Product, ProductImage
from .admin_views import import_products, download_import_template
from .widgets import HierarchicalCategorySelect


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'order']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['get_hierarchical_name',
                    'parent', 'order', 'is_active', 'created_at']
    list_filter = ['is_active', 'parent']
    search_fields = ['name']
    list_editable = ['order', 'is_active']
    ordering = ['parent__name', 'name', 'order']
    prepopulated_fields = {'slug': ('name',)}

    def get_hierarchical_name(self, obj):
        """Отображает иерархическое название категории"""
        if obj.parent:
            return f"{'　' * obj.get_ancestors().count()}{obj.name}"
        return obj.name
    get_hierarchical_name.short_description = 'Название'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'parent':
            kwargs['widget'] = HierarchicalCategorySelect(
                attrs={'class': 'form-control'})
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'article', 'category', 'subcategory',
                    'availability', 'is_active', 'views_count', 'created_at']
    list_filter = ['is_active', 'availability', 'category', 'subcategory']
    search_fields = ['title', 'article', 'description']
    list_editable = ['is_active', 'availability']
    ordering = ['-created_at']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ProductImageInline]

    change_list_template = 'admin/catalog/product_change_list.html'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name in ['category', 'subcategory']:
            kwargs['widget'] = HierarchicalCategorySelect(
                attrs={'class': 'form-control'})
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import/', import_products, name='catalog_product_import'),
            path('import-template/', download_import_template,
                 name='download_import_template'),
        ]
        return custom_urls + urls

    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'article', 'slug', 'category', 'subcategory')
        }),
        ('Описание', {
            'fields': ('description',)
        }),
        ('Характеристики', {
            'fields': ('details',)
        }),
        ('Изображения', {
            'fields': ('preview_image',)
        }),
        ('Статус', {
            'fields': ('availability', 'is_active')
        }),
        ('Статистика', {
            'fields': ('views_count',),
            'classes': ('collapse',)
        }),
    )


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'image', 'order', 'created_at']
    list_filter = ['product']
    list_editable = ['order']
    ordering = ['order']
