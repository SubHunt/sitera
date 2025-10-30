from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Category(models.Model):
    """Модель категории товаров"""
    name = models.CharField(max_length=255, verbose_name="Название")
    slug = models.SlugField(max_length=255, unique=True, verbose_name="URL")
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name="Родительская категория"
    )
    description = models.TextField(blank=True, verbose_name="Описание")
    order = models.PositiveIntegerField(
        default=0, verbose_name="Порядок сортировки")
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('catalog:category', kwargs={'slug': self.slug})


class Product(models.Model):
    """Модель товара"""
    AVAILABILITY_CHOICES = [
        ('in_stock', 'В наличии'),
        ('order', 'Под заказ'),
    ]

    title = models.CharField(max_length=255, verbose_name="Название")
    article = models.CharField(
        max_length=100, blank=True, verbose_name="Артикул")
    slug = models.SlugField(max_length=255, unique=True, verbose_name="URL")
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name="Категория"
    )
    subcategory = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subcategory_products',
        verbose_name="Подкатегория"
    )
    description = models.TextField(verbose_name="Описание")
    details = models.JSONField(
        default=dict, blank=True, verbose_name="Характеристики")
    preview_image = models.ImageField(
        upload_to='products/previews/',
        blank=True,
        null=True,
        verbose_name="Главное фото"
    )
    availability = models.CharField(
        max_length=20,
        choices=AVAILABILITY_CHOICES,
        default='in_stock',
        verbose_name="Наличие"
    )
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    views_count = models.PositiveIntegerField(
        default=0, verbose_name="Счетчик просмотров")
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('catalog:product', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class ProductImage(models.Model):
    """Модель дополнительных изображений товара"""
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name="Товар"
    )
    image = models.ImageField(
        upload_to='products/images/', verbose_name="Изображение")
    order = models.PositiveIntegerField(
        default=0, verbose_name="Порядок отображения")
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Создано")

    class Meta:
        verbose_name = "Изображение товара"
        verbose_name_plural = "Изображения товаров"
        ordering = ['order']

    def __str__(self):
        return f"Изображение для {self.product.title}"
