from django.core.management.base import BaseCommand
from apps.catalog.models import Category


class Command(BaseCommand):
    help = 'Восстанавливает исходные изображения категорий'

    def handle(self, *args, **options):
        # Исходный маппинг категорий с изображениями
        category_image_mapping = {
            'AV-коммутаторы': 'categories/av-switching.svg',
            'Архивные модели': 'categories/archived-models.svg',
            'Видеоконференцсвязь': 'categories/video-conference.svg',
            'Видеостены и LED-экраны': 'categories/video-walls.svg',
            'Готовые комплекты оборудования': 'categories/complete-kits.svg',
            'Аудиосистемы': 'categories/audio-systems.svg',
            'Документ-камеры': 'categories/document-cameras.svg',
            'Интерактивное оборудование': 'categories/interactive-devices.svg',
            'Интерактивные доски': 'categories/interactive-devices.svg',
            'Кабели': 'categories/cables.svg',
            'Камеры для видеоконференцсвязи': 'categories/cameras.svg',
            'Крепления для LED': 'categories/video-walls.svg',
            'Крепления': 'categories/mounts.svg',
            'Лицензии для видеоконференцсвязи': 'categories/video-walls.svg',
            'Микрофоны': 'categories/microphones.svg',
            'Наушники': 'categories/headphones.svg',
            'Системы звукового усиления': 'categories/sound-amplification.svg',
            'Системы управления': 'categories/control-equipment.svg',
            'Микрофонные системы': 'categories/microphones.svg',
            'Проекторы': 'categories/projectors.svg',
            'Оборудование для переговорных комнат': 'categories/meeting-rooms.svg',
            'Осветительное оборудование': 'categories/lighting-equipment.svg',
            'Системы Digital Signage': 'categories/digital-signage.svg',
            'Акустические системы': 'categories/audio-systems.svg',
            'Системы синхронного перевода': 'categories/sync-translation.svg',
            'Сценическое оборудование': 'categories/stage-effects.svg',
            'Трибуны и стойки': 'categories/podiums-racks.svg',
            'LED-экраны': 'categories/video-walls.svg',
            'Шоу-оборудование': 'categories/show-equipment.svg',
            'Конференц-системы': 'categories/conference-systems.svg',
            'Оборудование для видеоконференцсвязи': 'categories/video-conference.svg',
            'Системы голосования и записи': 'categories/microphones.svg',
            'Профессиональные дисплеи': 'categories/professional-displays.svg',
            'LED-экраны': 'categories/led-screens.svg'
        }

        self.stdout.write("Восстановление изображений категорий...")
        self.stdout.write("=" * 50)

        categories = Category.objects.all()
        restored_count = 0

        for category in categories:
            # Ищем соответствующее изображение в маппинге
            image_path = category_image_mapping.get(category.name)

            if image_path:
                old_image = category.image.name if category.image else None
                category.image.name = image_path
                category.save()

                self.stdout.write(
                    f"Восстановлена категория '{category.name}': {old_image} -> {image_path}")
                restored_count += 1
            else:
                self.stdout.write(
                    f"Пропущена категория '{category.name}': нет в маппинге")

        self.stdout.write("=" * 50)
        self.stdout.write(f"Восстановлено категорий: {restored_count}")
        self.stdout.write("Исходные изображения категорий восстановлены")
