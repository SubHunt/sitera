#!/usr/bin/env python
from apps.catalog.models import Category
import os
import sys
import django

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Устанавливаем настройки Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

# Инициализируем Django
django.setup()


def check_category_images():
    print("Проверка изображений категорий:")
    print("=" * 50)

    categories = Category.objects.all()

    for category in categories:
        if category.image:
            print(f"✓ {category.name}: {category.image.url}")
        else:
            print(f"✗ {category.name}: Нет изображения")

    print("=" * 50)
    print(f"Всего категорий: {categories.count()}")
    with_images = categories.exclude(image__isnull=True).exclude(image='')
    print(f"Категорий с изображениями: {with_images.count()}")
    without_images = categories.filter(
        image__isnull=True) | categories.filter(image='')
    print(f"Категорий без изображений: {without_images.count()}")


if __name__ == '__main__':
    check_category_images()
