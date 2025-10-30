from django.core.management.base import BaseCommand
from django.db import transaction
from apps.catalog.models import Category, Product, ProductImage
from apps.contacts.models import ContactRequest


class Command(BaseCommand):
    help = 'Очистка тестовых данных из базы данных'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Подтверждение удаления без дополнительного запроса',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            confirm = input(
                'Вы уверены, что хотите удалить все тестовые данные? (yes/no): '
            )
            if confirm.lower() != 'yes':
                self.stdout.write(self.style.ERROR('Операция отменена'))
                return

        with transaction.atomic():
            # Удаляем изображения товаров
            images_count = ProductImage.objects.count()
            ProductImage.objects.all().delete()
            self.stdout.write(f'Удалено изображений товаров: {images_count}')

            # Удаляем товары
            products_count = Product.objects.count()
            Product.objects.all().delete()
            self.stdout.write(f'Удалено товаров: {products_count}')

            # Удаляем категории
            categories_count = Category.objects.count()
            Category.objects.all().delete()
            self.stdout.write(f'Удалено категорий: {categories_count}')

            # Удаляем запросы КП
            requests_count = ContactRequest.objects.count()
            ContactRequest.objects.all().delete()
            self.stdout.write(f'Удалено запросов КП: {requests_count}')

            self.stdout.write(self.style.SUCCESS(
                'Все тестовые данные успешно удалены'))
