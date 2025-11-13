from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify
from apps.catalog.models import Category, Product, ProductImage
import json
import os
from django.conf import settings


class Command(BaseCommand):
    help = 'Создание тестовых данных для каталога'

    def handle(self, *args, **options):
        with transaction.atomic():
            self.create_categories()
            self.create_products()
            self.stdout.write(self.style.SUCCESS(
                'Тестовые данные успешно созданы'))

    def create_categories(self):
        """Создание основных категорий"""
        categories_data = [
            {
                'name': 'Конференц-системы',
                'slug': 'konferents-sistemy',
                'description': 'Оборудование для проведения конференций и совещаний',
                'image': 'categories/sync-translation.svg',
                'order': 1,
                'subcategories': [
                    {
                        'name': 'Системы синхронного перевода',
                        'slug': 'sistemy-sinhronnogo-perevoda'
                    },
                    {
                        'name': 'Дискуссионные системы',
                        'slug': 'diskussionnye-sistemy'
                    },
                    {
                        'name': 'Системы голосования',
                        'slug': 'sistemy-golosovaniya'
                    }
                ]
            },
            {
                'name': 'Оборудование для видеоконференцсвязи',
                'slug': 'oborudovanie-dlya-videokonferentssvyazi',
                'description': 'Оборудование для видеоконференцсвязи и удаленных совещаний',
                'image': 'categories/video-conference.svg',
                'order': 2,
                'subcategories': [
                    {
                        'name': 'Видеоконференцтерминалы',
                        'slug': 'videokonferentsterminaly'
                    },
                    {
                        'name': 'Камеры для ВКС',
                        'slug': 'kamery-dlya-vks'
                    },
                    {
                        'name': 'Решения для переговорных комнат',
                        'slug': 'resheniya-dlya-peregovornyh-komnat'
                    }
                ]
            },
            {
                'name': 'Микрофонные системы и микрофоны',
                'slug': 'mikrofonnye-sistemy-i-mikrofony',
                'description': 'Профессиональные микрофоны и микрофонные системы',
                'image': 'categories/microphones.svg',
                'order': 3,
                'subcategories': [
                    {
                        'name': 'Ручные микрофоны',
                        'slug': 'ruchnye-mikrofony'
                    },
                    {
                        'name': 'Настольные микрофоны',
                        'slug': 'nastolnye-mikrofony'
                    },
                    {
                        'name': 'Петличные микрофоны',
                        'slug': 'petlichnye-mikrofony'
                    }
                ]
            },
            {
                'name': 'Профессиональные дисплеи',
                'slug': 'professionalnye-displei',
                'description': 'Профессиональные дисплеи и мониторы',
                'image': 'categories/video-walls.svg',
                'order': 4,
                'subcategories': [
                    {
                        'name': 'Интерактивные панели',
                        'slug': 'interaktivnye-paneli'
                    },
                    {
                        'name': 'Мониторы для видеонаблюдения',
                        'slug': 'monitory-dlya-videonablyudeniya'
                    },
                    {
                        'name': 'Медицинские мониторы',
                        'slug': 'meditsinskie-monitory'
                    }
                ]
            },
            {
                'name': 'Светодиодные экраны',
                'slug': 'svetodiodnye-ekrany',
                'description': 'Светодиодные экраны и видеостены',
                'image': 'categories/video-walls.svg',
                'order': 5,
                'subcategories': [
                    {
                        'name': 'Внутренние LED-экраны',
                        'slug': 'vnutrennie-led-ekrany'
                    },
                    {
                        'name': 'Уличные LED-экраны',
                        'slug': 'ulichnye-led-ekrany'
                    },
                    {
                        'name': 'Контроллеры для LED',
                        'slug': 'kontrollery-dlya-led'
                    }
                ]
            }
        ]

        for cat_data in categories_data:
            # Создаем родительскую категорию
            category, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults={
                    'name': cat_data['name'],
                    'description': cat_data['description'],
                    'image': cat_data.get('image', ''),
                    'order': cat_data['order']
                }
            )

            if created:
                self.stdout.write(f"Создана категория: {category.name}")

            # Создаем подкатегории
            for subcat_data in cat_data.get('subcategories', []):
                subcategory, created = Category.objects.get_or_create(
                    slug=subcat_data['slug'],
                    defaults={
                        'name': subcat_data['name'],
                        'parent': category
                    }
                )

                if created:
                    self.stdout.write(
                        f"Создана подкатегория: {subcategory.name}")

    def create_products(self):
        """Создание тестовых товаров"""
        products_data = [
            # Конференц-системы - Системы синхронного перевода
            {
                'title': 'Система синхронного перевода Bosch Integrus 3',
                'article': 'BOS-INT-3',
                'category_slug': 'konferents-sistemy',
                'subcategory_slug': 'sistemy-sinhronnogo-perevoda',
                'description': 'Профессиональная система синхронного перевода для конференц-залов. Поддерживает до 31 языка перевода одновременно.',
                'details': {
                    'Производитель': 'Bosch',
                    'Количество каналов': '31',
                    'Дальность действия': '100м',
                    'Время работы': '12 часов',
                    'Частота': '2.4 ГГц',
                    'Мощность': '10мВт'
                },
                'availability': 'in_stock'
            },
            {
                'title': 'Портативная система перевода Williams Sound Digi-Wave',
                'article': 'WS-DW-400',
                'category_slug': 'konferents-sistemy',
                'subcategory_slug': 'sistemy-sinhronnogo-perevoda',
                'description': 'Портативная система синхронного перевода для конференций и мероприятий. Поддерживает до 4 языков перевода.',
                'details': {
                    'Производитель': 'Williams Sound',
                    'Количество каналов': '4',
                    'Дальность действия': '60м',
                    'Время работы': '14 часов',
                    'Частота': '2.4 ГГц',
                    'Мощность': '10мВт'
                },
                'availability': 'in_stock'
            },
            {
                'title': 'Наушники для системы перевода Sennheiser HDE 2020-D',
                'article': 'SEN-HDE-2020',
                'category_slug': 'konferents-sistemy',
                'subcategory_slug': 'sistemy-sinhronnogo-perevoda',
                'description': 'Профессиональные стереонаушники для систем синхронного перевода с инфракрасным приемником.',
                'details': {
                    'Производитель': 'Sennheiser',
                    'Тип': 'Накладные',
                    'Чувствительность': '108 дБ',
                    'Сопротивление': '32 Ом',
                    'Частотный диапазон': '18-20000 Гц'
                },
                'availability': 'in_stock'
            },

            # Оборудование для видеоконференцсвязи
            {
                'title': 'Видеоконференцтерминал Polycom RealPresence Group 700',
                'article': 'GRP7000',
                'category_slug': 'oborudovanie-dlya-videokonferentssvyazi',
                'subcategory_slug': 'videokonferentsterminaly',
                'description': 'Профессиональный видеоконференцтерминал для переговорных комнат среднего и крупного размера.',
                'details': {
                    'Производитель': 'Polycom',
                    'Разрешение': '4K',
                    'Количество участников': 'до 64',
                    'Протоколы': 'H.323, SIP',
                    'Скорость': 'до 4 Мбит/с',
                    'Интерфейсы': 'HDMI, USB, LAN'
                },
                'availability': 'in_stock'
            },
            {
                'title': 'Система ВКС Cisco SX80',
                'article': 'SX80',
                'category_slug': 'oborudovanie-dlya-videokonferentssvyazi',
                'subcategory_slug': 'videokonferentsterminaly',
                'description': 'Интегрированная система видеоконференцсвязи для больших переговорных комнат.',
                'details': {
                    'Производитель': 'Cisco',
                    'Разрешение': '1080p60',
                    'Количество экранов': '3',
                    'Протоколы': 'SIP, H.323',
                    'Скорость': 'до 6 Мбит/с',
                    'Кодеки': 'H.264, H.265'
                },
                'availability': 'in_stock'
            },
            {
                'title': 'PTZ камера Sony SRG-300SE',
                'article': 'SRG300SE',
                'category_slug': 'oborudovanie-dlya-videokonferentssvyazi',
                'subcategory_slug': 'kamery-dlya-vks',
                'description': 'Профессиональная PTZ камера с 30-кратным оптическим зумом для конференц-залов.',
                'details': {
                    'Производитель': 'Sony',
                    'Разрешение': '1080p',
                    'Оптический зум': '30x',
                    'Цифровой зум': '12x',
                    'Управление': 'VISCA',
                    'Интерфейсы': 'HDMI, 3G-SDI, IP'
                },
                'availability': 'in_stock'
            },

            # Микрофонные системы и микрофоны
            {
                'title': 'Потолочный микрофон Shure MXA910',
                'article': 'MXA910',
                'category_slug': 'mikrofonnye-sistemy-i-mikrofony',
                'subcategory_slug': 'nastolnye-mikrofony',
                'description': 'Потолочный массивный микрофон с автоматической наведением на говорящего.',
                'details': {
                    'Производитель': 'Shure',
                    'Тип': 'Массивный потолочный',
                    'Количество капсюлей': '8',
                    'Направленность': 'Автоматическая',
                    'Цвет': 'Белый, Черный',
                    'Установка': 'Подвесной'
                },
                'availability': 'order'
            },
            {
                'title': 'Ручной микрофон Sennheiser e945',
                'article': 'SEN-E945',
                'category_slug': 'mikrofonnye-sistemy-i-mikrofony',
                'subcategory_slug': 'ruchnye-mikrofony',
                'description': 'Профессиональный динамический вокальный микрофон с супекардиоидной характеристикой.',
                'details': {
                    'Производитель': 'Sennheiser',
                    'Тип': 'Динамический',
                    'Направленность': 'Суперкардиоидная',
                    'Частотный диапазон': '40-18000 Гц',
                    'Чувствительность': '1.8 мВ/Па',
                    'Разъем': 'XLR'
                },
                'availability': 'in_stock'
            },
            {
                'title': 'Петличный микрофон Sennheiser ME 2',
                'article': 'SEN-ME2',
                'category_slug': 'mikrofonnye-sistemy-i-mikrofony',
                'subcategory_slug': 'petlichnye-mikrofony',
                'description': 'Компактный петличный микрофон для систем конференцсвязи и выступлений.',
                'details': {
                    'Производитель': 'Sennheiser',
                    'Тип': 'Конденсаторный',
                    'Направленность': 'Всенаправленная',
                    'Частотный диапазон': '30-20000 Гц',
                    'Чувствительность': '10 мВ/Па',
                    'Разъем': 'Mini-lock'
                },
                'availability': 'in_stock'
            },

            # Профессиональные дисплеи
            {
                'title': 'Интерактивная панель Samsung Flip 85"',
                'article': 'SAM-FLIP-85',
                'category_slug': 'professionalnye-displei',
                'subcategory_slug': 'interaktivnye-paneli',
                'description': '85-дюймовая интерактивная панель для совещаний и презентаций с поддержкой одновременной работы 4 пользователей.',
                'details': {
                    'Производитель': 'Samsung',
                    'Диагональ': '85"',
                    'Разрешение': '4K UHD',
                    'Яркость': '300 кд/м²',
                    'Касания': 'До 4 одновременно',
                    'Подключение': 'HDMI, USB, Wi-Fi'
                },
                'availability': 'in_stock'
            },
            {
                'title': 'Профессиональный монитор EIZO ColorEdge CG319X',
                'article': 'EIZ-CG319X',
                'category_slug': 'professionalnye-displei',
                'subcategory_slug': 'monitory-dlya-videonablyudeniya',
                'description': '29.5-дюймовый профессиональный монитор с широким цветовым охватом для видеонаблюдения.',
                'details': {
                    'Производитель': 'EIZO',
                    'Диагональ': '29.5"',
                    'Разрешение': '2560×1080',
                    'Яркость': '400 кд/м²',
                    'Контрастность': '1000:1',
                    'Цветовой охват': '99% Adobe RGB'
                },
                'availability': 'order'
            },

            # Светодиодные экраны
            {
                'title': 'Внутренний LED-экран Absen A5',
                'article': 'ABS-A5-2.6',
                'category_slug': 'svetodiodnye-ekrany',
                'subcategory_slug': 'vnutrennie-led-ekrany',
                'description': 'Внутренний LED-экран с шагом пикселя 2.6мм для создания бесшовных видеостен.',
                'details': {
                    'Производитель': 'Absen',
                    'Шаг пикселя': '2.6мм',
                    'Яркость': '1000 кд/м²',
                    'Разрешение модуля': '128×128',
                    'Обновление': '3840 Гц',
                    'Глубина цвета': '16 бит'
                },
                'availability': 'in_stock'
            },
            {
                'title': 'Контроллер LED-экранов Novastar VX4S',
                'article': 'NOV-VX4S',
                'category_slug': 'svetodiodnye-ekrany',
                'subcategory_slug': 'kontrollery-dlya-led',
                'description': 'Профессиональный контроллер для управления LED-экранами с поддержкой 4K разрешения.',
                'details': {
                    'Производитель': 'Novastar',
                    'Макс. разрешение': '1920×1200',
                    'Количество выходов': '4',
                    'Входы': 'DVI, HDMI, SDI',
                    'Глубина цвета': '12 бит',
                    'Обновление': '60 Гц'
                },
                'availability': 'in_stock'
            }
        ]

        for product_data in products_data:
            # Получаем категорию
            try:
                category = Category.objects.get(
                    slug=product_data['category_slug'])
            except Category.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(
                        f"Категория {product_data['category_slug']} не найдена")
                )
                continue

            # Получаем подкатегорию
            subcategory = None
            if product_data.get('subcategory_slug'):
                try:
                    subcategory = Category.objects.get(
                        slug=product_data['subcategory_slug'])
                except Category.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Подкатегория {product_data['subcategory_slug']} не найдена")
                    )

            # Создаем товар
            product, created = Product.objects.get_or_create(
                article=product_data['article'],
                defaults={
                    'title': product_data['title'],
                    'slug': slugify(product_data['title']),
                    'category': category,
                    'subcategory': subcategory,
                    'description': product_data['description'],
                    'details': product_data['details'],
                    'availability': product_data['availability']
                }
            )

            if created:
                self.stdout.write(f"Создан товар: {product.title}")
            else:
                # Обновляем существующий товар
                product.title = product_data['title']
                product.category = category
                product.subcategory = subcategory
                product.description = product_data['description']
                product.details = product_data['details']
                product.availability = product_data['availability']
                product.save()
                self.stdout.write(f"Обновлен товар: {product.title}")
