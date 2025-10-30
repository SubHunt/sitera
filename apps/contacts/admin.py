from django.contrib import admin
from .models import ContactRequest


@admin.register(ContactRequest)
class ContactRequestAdmin(admin.ModelAdmin):
    list_display = ['name', 'organization', 'phone', 'email',
                    'request_type', 'product', 'is_processed', 'created_at']
    list_filter = ['request_type', 'is_processed', 'created_at']
    search_fields = ['name', 'organization', 'phone', 'email', 'message']
    list_editable = ['is_processed']
    ordering = ['-created_at']
    readonly_fields = ['created_at']

    fieldsets = (
        ('Контактная информация', {
            'fields': ('name', 'organization', 'phone', 'email')
        }),
        ('Детали запроса', {
            'fields': ('request_type', 'product', 'message')
        }),
        ('Статус', {
            'fields': ('is_processed',)
        }),
        ('Системная информация', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(is_processed=False)
