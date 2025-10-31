from django.core.management.base import BaseCommand
from django.db import connection
from django.core.files import File
import json
import os


class Command(BaseCommand):
    help = 'Восстановление данных в PostgreSQL из backup файла'

    def handle(self, *args, **options):
        # Проверяем текущее подключение
        self.stdout.write('Текущая база данных: ' + connection.vendor)

        if connection.vendor != 'postgresql':
            self.stdout.write(self.style.ERROR(
                'Сначала настройте подключение к PostgreSQL в .env файле'))
            return

        # Проверяем наличие backup файла
        if not os.path.exists('db_backup.json'):
            self.stdout.write(self.style.ERROR(
                'Файл db_backup.json не найден. Сначала выполните migrate_to_postgresql'))
            return

        # Загружаем данные из файла
        with open('db_backup.json', 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.stdout.write('Восстановление данных...')

        # Восстанавливаем категории
        from apps.catalog.models import Category
        from apps.contacts.models import ContactRequest

        category_map = {}

        for cat_data in data['categories']:
            category, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults={
                    'name': cat_data['name'],
                    'description': cat_data['description'],
                }
            )

            # Восстанавливаем изображение если есть
            if cat_data['image'] and os.path.exists(cat_data['image']):
                with open(cat_data['image'], 'rb') as img_file:
                    category.image.save(os.path.basename(
                        cat_data['image']), File(img_file), save=True)

            category_map[cat_data['name']] = category
            self.stdout.write(
                f'Категория: {cat_data["name"]} - {"создана" if created else "найдена"}')

        # Восстанавливаем товары
        from apps.catalog.models import Product

        for prod_data in data['products']:
            category = category_map.get(
                prod_data['category']) if prod_data['category'] else None

            product, created = Product.objects.get_or_create(
                slug=prod_data['slug'],
                defaults={
                    'title': prod_data['title'],
                    'article': prod_data.get('article', ''),
                    'category': category,
                    'description': prod_data['description'],
                    'details': prod_data.get('details', {}),
                    'availability': prod_data.get('availability', 'in_stock'),
                    'is_active': prod_data.get('is_active', True),
                    'views_count': prod_data.get('views_count', 0),
                }
            )

            # Восстанавливаем изображение если есть
            if prod_data.get('preview_image') and os.path.exists(prod_data['preview_image']):
                with open(prod_data['preview_image'], 'rb') as img_file:
                    product.preview_image.save(os.path.basename(
                        prod_data['preview_image']), File(img_file), save=True)

            self.stdout.write(
                f'Товар: {prod_data["title"]} - {"создан" if created else "найден"}')

        # Восстанавливаем контакты
        for cont_data in data['contacts']:
            contact, created = Contact.objects.get_or_create(
                email=cont_data['email'],
                defaults={
                    'name': cont_data['name'],
                    'phone': cont_data['phone'],
                    'message': cont_data['message'],
                }
            )
            self.stdout.write(
                f'Контакт: {cont_data["name"]} - {"создан" if created else "найден"}')

        self.stdout.write(self.style.SUCCESS(
            'Данные успешно восстановлены в PostgreSQL'))
