from django.core.management.base import BaseCommand
from django.db import connection, connections
from django.conf import settings
import os


class Command(BaseCommand):
    help = 'Перенос данных из SQLite в PostgreSQL'

    def handle(self, *args, **options):
        # Проверяем текущее подключение
        self.stdout.write('Текущая база данных: ' + connection.vendor)

        if connection.vendor == 'postgresql':
            self.stdout.write(self.style.SUCCESS(
                'Уже используется PostgreSQL'))
            return

        # Создаем backup SQLite данных
        self.stdout.write('Создание backup данных...')

        # Получаем все данные из SQLite
        from apps.catalog.models import Category, Product
        from apps.contacts.models import ContactRequest

        categories = list(Category.objects.all())
        products = list(Product.objects.all())
        contacts = list(ContactRequest.objects.all())

        self.stdout.write(f'Найдено категорий: {len(categories)}')
        self.stdout.write(f'Найдено товаров: {len(products)}')
        self.stdout.write(f'Найдено контактов: {len(contacts)}')

        # Сохраняем данные в файл
        import json
        data = {
            'categories': [
                {
                    'name': cat.name,
                    'slug': cat.slug,
                    'description': cat.description,
                    'image': str(cat.image) if cat.image else None,
                } for cat in categories
            ],
            'products': [
                {
                    'title': prod.title,
                    'article': prod.article,
                    'slug': prod.slug,
                    'category': prod.category.name if prod.category else None,
                    'subcategory': prod.subcategory.name if prod.subcategory else None,
                    'description': prod.description,
                    'details': prod.details,
                    'preview_image': str(prod.preview_image) if prod.preview_image else None,
                    'availability': prod.availability,
                    'is_active': prod.is_active,
                    'views_count': prod.views_count,
                } for prod in products
            ],
            'contacts': [
                {
                    'name': cont.name,
                    'organization': cont.organization,
                    'phone': cont.phone,
                    'email': cont.email,
                    'request_type': cont.request_type,
                    'product': cont.product.name if cont.product else None,
                    'message': cont.message,
                    'is_processed': cont.is_processed,
                } for cont in contacts
            ]
        }

        with open('db_backup.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        self.stdout.write(self.style.SUCCESS(
            'Данные сохранены в db_backup.json'))
        self.stdout.write(self.style.WARNING(
            'Теперь измените .env файл для подключения к PostgreSQL и выполните migrate_to_postgresql_restore'))
