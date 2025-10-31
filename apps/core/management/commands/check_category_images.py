from django.core.management.base import BaseCommand
from apps.catalog.models import Category


class Command(BaseCommand):
    help = 'Проверяет изображения категорий'

    def handle(self, *args, **options):
        self.stdout.write("Проверка изображений категорий:")
        self.stdout.write("=" * 50)

        categories = Category.objects.all()

        for category in categories:
            if category.image:
                self.stdout.write(f"+ {category.name}: {category.image.url}")
            else:
                self.stdout.write(f"- {category.name}: Нет изображения")

        self.stdout.write("=" * 50)
        self.stdout.write(f"Всего категорий: {categories.count()}")
        with_images = categories.exclude(image__isnull=True).exclude(image='')
        self.stdout.write(f"Категорий с изображениями: {with_images.count()}")
        without_images = categories.filter(
            image__isnull=True) | categories.filter(image='')
        self.stdout.write(
            f"Категорий без изображений: {without_images.count()}")
