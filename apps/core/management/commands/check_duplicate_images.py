from django.core.management.base import BaseCommand
from apps.catalog.models import Category
from collections import defaultdict


class Command(BaseCommand):
    help = 'Проверяет дублирующиеся изображения категорий'

    def handle(self, *args, **options):
        categories = Category.objects.all()
        used_images = defaultdict(list)

        for cat in categories:
            if cat.image and cat.image.name:
                img_name = cat.image.name.split('/')[-1]
                used_images[img_name].append(cat.name)

        self.stdout.write(self.style.SUCCESS('Используемые изображения:'))

        duplicates_found = False
        for img, cats in used_images.items():
            if len(cats) > 1:
                duplicates_found = True
                self.stdout.write(self.style.WARNING(
                    f'{img}: {", ".join(cats)}'))

        if not duplicates_found:
            self.stdout.write(self.style.SUCCESS(
                'Дублирующихся изображений не найдено!'))

        # Выводим все категории и их изображения
        self.stdout.write('\nВсе категории и их изображения:')
        for cat in categories:
            if cat.image and cat.image.name:
                img_name = cat.image.name.split('/')[-1]
                self.stdout.write(f'{cat.name}: {img_name}')
