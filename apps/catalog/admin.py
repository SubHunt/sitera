from django.contrib import admin
from .models import Category, Product, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'order']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'order', 'is_active', 'created_at']
    list_filter = ['is_active', 'parent']
    search_fields = ['name']
    list_editable = ['order', 'is_active']
    ordering = ['order', 'name']
    prepopulated_fields = {'slug': ('name',)}


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
