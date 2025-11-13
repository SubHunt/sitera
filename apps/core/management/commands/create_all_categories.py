from django.core.management.base import BaseCommand
from apps.catalog.models import Category


class Command(BaseCommand):
    help = 'Create all categories for the catalog'

    def handle(self, *args, **options):
        categories_data = [
            {
                'name': 'Конференц-системы',
                'slug': 'konferents-sistemy',
                'description': 'Оборудование для проведения конференций и совещаний'
            },
            {
                'name': 'Системы синхронного перевода',
                'slug': 'sistemy-sinhronnogo-perevoda',
                'description': 'Профессиональное оборудование для синхронного перевода'
            },
            {
                'name': 'Оборудование для видеоконференцсвязи',
                'slug': 'oborudovanie-dlya-videokonferentssvyazi',
                'description': 'Системы для видеоконференций и онлайн-совещаний'
            },
            {
                'name': 'Микрофонные системы и микрофоны',
                'slug': 'mikrofonnye-sistemy-i-mikrofony',
                'description': 'Профессиональные микрофоны и микрофонные системы'
            },
            {
                'name': 'Наушники',
                'slug': 'naushniki',
                'description': 'Профессиональные наушники для конференц-залов'
            },
            {
                'name': 'Оборудование звукоусиления',
                'slug': 'oborudovanie-zukousileniya',
                'description': 'Системы звукоусиления для конференц-залов и помещений'
            },
            {
                'name': 'Профессиональные дисплеи',
                'slug': 'professionalnye-displei',
                'description': 'Высококачественные дисплеи для профессионального использования'
            },
            {
                'name': 'Светодиодные экраны',
                'slug': 'svetodiodnye-ekrany',
                'description': 'LED-экраны и видеостены для различных применений'
            },
            {
                'name': 'Проекторы',
                'slug': 'proektory',
                'description': 'Профессиональные проекторы для конференц-залов'
            },
            {
                'name': 'Интерактивные устройства',
                'slug': 'interaktivnye-ustroistva',
                'description': 'Интерактивные доски, панели и дисплеи'
            },
            {
                'name': 'Системы Digital Signage',
                'slug': 'sistemy-digital-signage',
                'description': 'Цифровые системы информирования и рекламы'
            },
            {
                'name': 'Видеокамеры и устройства записи',
                'slug': 'videokamery-i-ustroistva-zapisi',
                'description': 'Профессиональные видеокамеры и оборудование для записи'
            },
            {
                'name': 'Документ-камеры',
                'slug': 'dokument-kamery',
                'description': 'Цифровые документ-камеры для презентаций'
            },
            {
                'name': 'Решения для переговорных комнат',
                'slug': 'resheniya-dlya-peregovornykh-komnat',
                'description': 'Комплексные решения для оборудования переговорных комнат'
            },
            {
                'name': 'AV-коммутация',
                'slug': 'av-kommutatsiya',
                'description': 'Коммутационное AV-оборудование'
            },
            {
                'name': 'Оборудование управления',
                'slug': 'oborudovanie-upravleniya',
                'description': 'Системы управления AV-оборудованием'
            },
            {
                'name': 'Шоу-оборудование',
                'slug': 'shou-oborudovanie',
                'description': 'Профессиональное оборудование для шоу и мероприятий'
            },
            {
                'name': 'Световое оборудование',
                'slug': 'svetovoe-oborudovanie',
                'description': 'Профессиональное световое оборудование'
            },
            {
                'name': 'Сценические спецэффекты',
                'slug': 'stsenicheskie-spetseffekty',
                'description': 'Оборудование для создания сценических спецэффектов'
            },
            {
                'name': 'Крепления',
                'slug': 'krepleniya',
                'description': 'Крепления и монтажные аксессуары'
            },
            {
                'name': 'Готовые комплекты оборудования',
                'slug': 'gotovye-komplekty-oborudovaniya',
                'description': 'Готовые комплекты оборудования для различных задач'
            },
            {
                'name': 'Кабели',
                'slug': 'kabeli',
                'description': 'Профессиональные кабели и соединители'
            },
            {
                'name': 'Трибуны и рэковые шкафы',
                'slug': 'tribuny-i-rekovye-shkafy',
                'description': 'Профессиональные трибуны и рэковые шкафы'
            },
            {
                'name': 'Архивные модели',
                'slug': 'arkhivnye-modeli',
                'description': 'Архивные модели оборудования со скидками'
            }
        ]

        created_count = 0
        updated_count = 0

        for category_data in categories_data:
            category, created = Category.objects.update_or_create(
                slug=category_data['slug'],
                defaults={
                    'name': category_data['name'],
                    'description': category_data['description']
                }
            )

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created category: {category.name}')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Updated category: {category.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully processed {created_count + updated_count} categories '
                f'({created_count} created, {updated_count} updated)'
            )
        )
