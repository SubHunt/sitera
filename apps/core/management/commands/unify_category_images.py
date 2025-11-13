from django.core.management.base import BaseCommand
from apps.catalog.models import Category
import os


class Command(BaseCommand):
    help = 'Обновляет все категории чтобы использовать 4 рабочих изображения без текста'

    def handle(self, *args, **options):
        # 4 рабочих изображения без текста
        working_images = [
            'categories/sound-amplification.svg',
            'categories/conference-systems.svg',
            'categories/professional-displays.svg',
            'categories/led-screens.svg'
        ]

        self.stdout.write("Обновление изображений категорий...")
        self.stdout.write("=" * 50)

        categories = Category.objects.all()
        updated_count = 0

        for i, category in enumerate(categories):
            # Выбираем изображение по кругу
            image_path = working_images[i % len(working_images)]

            # Обновляем путь к изображению
            old_image = category.image.name if category.image else None
            category.image.name = image_path
            category.save()

            self.stdout.write(
                f"Обновлена категория '{category.name}': {old_image} -> {image_path}")
            updated_count += 1

        self.stdout.write("=" * 50)
        self.stdout.write(f"Обновлено категорий: {updated_count}")
        self.stdout.write(
            "Все категории теперь используют 4 рабочих изображения без текста")
