from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class ContactRequest(models.Model):
    """Модель запроса коммерческого предложения"""
    REQUEST_TYPE_CHOICES = [
        ('kp', 'КП'),
        ('consultation', 'Консультация'),
        ('support', 'Поддержка'),
    ]

    name = models.CharField(max_length=255, verbose_name="Имя")
    organization = models.CharField(
        max_length=255, blank=True, verbose_name="Организация")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    email = models.EmailField(blank=True, verbose_name="Email")
    request_type = models.CharField(
        max_length=20,
        choices=REQUEST_TYPE_CHOICES,
        default='kp',
        verbose_name="Тип запроса"
    )
    product = models.ForeignKey(
        'catalog.Product',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Товар"
    )
    message = models.TextField(verbose_name="Сообщение")
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Создано")
    is_processed = models.BooleanField(
        default=False, verbose_name="Обработано")

    class Meta:
        verbose_name = "Запрос КП"
        verbose_name_plural = "Запросы КП"
        ordering = ['-created_at']

    def __str__(self):
        return f"Запрос от {self.name} ({self.get_request_type_display()})"
