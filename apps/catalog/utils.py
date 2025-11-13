import csv
import json
import pandas as pd
import re
import requests
import io
import os
from io import BytesIO, StringIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils.text import slugify
from urllib.parse import urlparse
from .models import Product, Category, ProductImage

# Создаем сессию для повторного использования TCP-соединений
SESSION = requests.Session()
# Устанавливаем адаптер с увеличенным количеством подключений
adapter = requests.adapters.HTTPAdapter(
    pool_connections=10,
    pool_maxsize=20,
    max_retries=2
)
SESSION.mount('http://', adapter)
SESSION.mount('https://', adapter)


# Глобальная переменная для хранения прогресса импорта
IMPORT_PROGRESS = {
    'processed': 0,
    'total': 0,
    'percentage': 0,
    'cancelled': False
}


class ImportProcessor:
    def __init__(self, file, category_id=None, update_existing=False, delete_missing=False):
        self.file = file
        self.category_id = category_id
        self.update_existing = update_existing
        self.delete_missing = delete_missing
        self.errors = []
        self.warnings = []
        self.imported_count = 0
        self.updated_count = 0
        self.skipped_count = 0
        self.total_rows = 0
        self.processed_rows = 0
        self.downloaded_images = 0
        self.total_images = 0
        self.progress_callback = None

        # Сброс прогресса при начале нового импорта
        global IMPORT_PROGRESS
        IMPORT_PROGRESS = {
            'processed': 0,
            'total': 0,
            'percentage': 0,
            'cancelled': False
        }

    def set_progress_callback(self, callback):
        """Установка callback функции для отслеживания прогресса"""
        self.progress_callback = callback

    def process_file(self):
        """Определяет формат файла и запускает соответствующий обработчик"""
        file_extension = self.file.name.split('.')[-1].lower()

        if file_extension == 'csv':
            return self._process_csv()
        elif file_extension in ['xlsx', 'xls']:
            return self._process_excel()
        elif file_extension == 'json':
            return self._process_json()
        else:
            self.errors.append(
                f"Неподдерживаемый формат файла: {file_extension}")
            return False

    def _process_csv(self):
        """Обработка CSV файла"""
        try:
            # Читаем файл в текстовом режиме
            if hasattr(self.file, 'read'):
                content = self.file.read()
                if isinstance(content, bytes):
                    content = content.decode('utf-8')
                csv_file = StringIO(content)
            else:
                csv_file = self.file

            reader = csv.DictReader(csv_file)
            return self._process_data_rows(reader)
        except Exception as e:
            self.errors.append(f"Ошибка при чтении CSV файла: {str(e)}")
            return False

    def _process_excel(self):
        """Обработка Excel файла"""
        try:
            # Читаем файл
            if hasattr(self.file, 'read'):
                content = self.file.read()
                df = pd.read_excel(BytesIO(content))
            else:
                df = pd.read_excel(self.file)

            # Конвертируем DataFrame в список словарей
            data = df.to_dict('records')
            return self._process_data_rows(data)
        except Exception as e:
            self.errors.append(f"Ошибка при чтении Excel файла: {str(e)}")
            return False

    def _process_json(self):
        """Обработка JSON файла"""
        try:
            # Читаем файл
            if hasattr(self.file, 'read'):
                content = self.file.read()
                if isinstance(content, bytes):
                    content = content.decode('utf-8')
                data = json.loads(content)
            else:
                data = json.load(self.file)

            # Убедимся, что data - это список
            if isinstance(data, dict):
                # Если один товар
                data = [data]
            elif not isinstance(data, list):
                # Если что-то другое (не массив и не словарь)
                self.errors.append(
                    f"Некорректный формат JSON: ожидается массив или объект, получен {type(data).__name__}")
                return False

            return self._process_data_rows(data)
        except json.JSONDecodeError as e:
            self.errors.append(f"Ошибка парсинга JSON: {str(e)}")
            return False
        except Exception as e:
            self.errors.append(f"Ошибка при чтении JSON файла: {str(e)}")
            return False

    def _process_data_rows(self, rows):
        """Обработка строк данных"""
        # Преобразуем rows в список, если это необходимо, чтобы получить общее количество
        rows_list = list(rows) if not isinstance(rows, list) else rows
        self.total_rows = len(rows_list)

        # Подсчитываем общее количество изображений для более точного прогресса
        self.total_images = 0
        for row in rows_list:
            if row.get('images'):
                images = row.get('images', [])
                if isinstance(images, str):
                    images = [images.strip()] if images.strip() else []
                self.total_images += len(images)

        try:
            # Сохраняем список существующих названий для проверки
            existing_titles = set(
                Product.objects.values_list('title', flat=True))
            processed_titles = set()

            # Итерируемся по списку строк
            for row_num, row in enumerate(rows_list, start=2):
                # Проверяем, не был ли отменен импорт
                if IMPORT_PROGRESS.get('cancelled', False):
                    self.warnings.append("Импорт был отменен пользователем")
                    return True  # Возвращаем True, так как отмена - это не ошибка

                # Увеличиваем счетчик обработанных строк
                self.processed_rows = row_num - 1

                # Обновляем прогресс
                self._update_progress()

                try:
                    result = self._process_single_row(row, row_num)
                    if result and row.get('title'):
                        processed_titles.add(str(row['title']).strip())
                except InterruptedError:
                    # Прерываем выполнение если импорт был отменен
                    self.warnings.append("Импорт был отменен пользователем")
                    return True  # Возвращаем True, так как отмена - это не ошибка
                except Exception as e:
                    self.errors.append(f"Строка {row_num}: {str(e)}")
                    continue

            # Удаляем отсутствующие товары если нужно
            if self.delete_missing and self.category_id:
                missing_titles = existing_titles - processed_titles
                deleted_count = Product.objects.filter(
                    title__in=missing_titles,
                    category_id=self.category_id
                ).delete()[0]
                if deleted_count > 0:
                    self.warnings.append(
                        f"Удалено {deleted_count} отсутствующих товаров")

            return True  # Возвращаем True даже если есть предупреждения

        except Exception as e:
            self.errors.append(f"Ошибка при обработке данных: {str(e)}")
            return False

    # def _process_single_row(self, row, row_num):
    #     """Обработка одной строки данных"""
    #     # Валидация обязательных полей
    #     title = str(row.get('title', '')).strip()
    #     if not title:
    #         self.warnings.append(
    #             f"Строка {row_num}: Пропущена (отсутствует название товара)")
    #         self.skipped_count += 1
    #         return False

    #     # Получаем артикул (может быть пустым)
    #     article = str(row.get('article', '')).strip(
    #     ) if row.get('article') else ''

    #     # Получаем категорию
    #     category = None
    #     if self.category_id:
    #         # Используем выбранную категорию из формы
    #         try:
    #             category = Category.objects.get(id=self.category_id)
    #         except Category.DoesNotExist:
    #             self.errors.append(
    #                 f"Строка {row_num}: Категория с ID {self.category_id} не найдена")
    #             self.skipped_count += 1
    #             return False
    #     elif row.get('category'):
    #         # Используем категорию из CSV
    #         category_name = str(row['category']).strip()
    #         try:
    #             category = Category.objects.get(name=category_name)
    #         except Category.DoesNotExist:
    #             self.warnings.append(
    #                 f"Строка {row_num}: Категория '{category_name}' не найдена. Выберите категорию в форме импорта.")
    #             self.skipped_count += 1
    #             return False
    #     else:
    #         self.warnings.append(f"Строка {row_num}: Не указана категория")
    #         self.skipped_count += 1
    #         return False

    #     # Обрабатываем описание
    #     description = str(row.get('description', '')).strip()
    #     # Удаляем "Описание " в начале если есть
    #     if description.startswith('Описание '):
    #         description = description[9:].strip()

    #     # Обрабатываем характеристики (details)
    #     details = self._parse_details(row.get('details', ''))

    #     # Обрабатываем availability
    #     availability = self._parse_availability(row.get('availability', ''))

    #     # Генерируем slug
    #     slug = self._generate_unique_slug(title, article)

    #     # Проверяем существование товара по НАЗВАНИЮ (title)
    #     product = None
    #     try:
    #         product = Product.objects.get(title=title)

    #         if self.update_existing:
    #             # Обновляем существующий товар
    #             product.article = article  # Обновляем артикул
    #             product.description = description
    #             product.details = details
    #             product.category = category
    #             product.availability = availability
    #             product.is_active = True

    #             # Обновляем preview_image
    #             if row.get('images'):
    #                 product.preview_image = str(row['images']).strip()

    #             product.save()
    #             self.updated_count += 1
    #             print(f"✅ Обновлен товар: {title}")
    #         else:
    #             self.warnings.append(
    #                 f"Строка {row_num}: Товар '{title}' уже существует, пропущен")
    #             self.skipped_count += 1
    #             return True

    #     except Product.DoesNotExist:
    #         product = None

    #     # Если товара нет - создаем новый
    #     if not product:
    #         try:
    #             product = Product.objects.create(
    #                 title=title,
    #                 article=article,
    #                 slug=slug,
    #                 description=description,
    #                 details=details,
    #                 category=category,
    #                 availability=availability,
    #                 is_active=True,
    #                 preview_image=str(row.get('images', '')
    #                                   ).strip() if row.get('images') else ''
    #             )
    #             self.imported_count += 1
    #             print(
    #                 f"✅ Создан товар: {title} (артикул: {article if article else 'нет'})")
    #         except Exception as e:
    #             self.errors.append(
    #                 f"Строка {row_num}: Ошибка создания товара '{title}' - {str(e)}")
    #             return False

    #     # Обработка дополнительных изображений из поля url
    #     if row.get('url'):
    #         self._process_additional_images(product, row['url'])

    #     return True
    def _process_single_row(self, row, row_num):
        """Обработка одной строки данных"""
        # Валидация обязательных полей
        title = str(row.get('title', '')).strip()
        if not title:
            self.warnings.append(
                f"Строка {row_num}: Пропущена (отсутствует название товара)")
            self.skipped_count += 1
            return False

        # Получаем артикул (может быть пустым)
        article = str(row.get('article', '')).strip(
        ) if row.get('article') else ''

        # Получаем категорию
        category = None
        if self.category_id:
            # Используем выбранную категорию из формы
            try:
                category = Category.objects.get(id=self.category_id)
            except Category.DoesNotExist:
                self.errors.append(
                    f"Строка {row_num}: Категория с ID {self.category_id} не найдена")
                self.skipped_count += 1
                return False
        elif row.get('category'):
            # Используем категорию из CSV
            category_name = str(row['category']).strip()
            try:
                category = Category.objects.get(name=category_name)
            except Category.DoesNotExist:
                self.warnings.append(
                    f"Строка {row_num}: Категория '{category_name}' не найдена. Выберите категорию в форме импорта.")
                self.skipped_count += 1
                return False
        else:
            self.warnings.append(f"Строка {row_num}: Не указана категория")
            self.skipped_count += 1
            return False

        # Обрабатываем описание
        description = str(row.get('description', '')).strip()
        # Удаляем "Описание " в начале если есть
        if description.startswith('Описание '):
            description = description[9:].strip()

        # Обрабатываем характеристики (details)
        details = self._parse_details(row.get('details', ''))

        # Обрабатываем availability
        availability = self._parse_availability(row.get('availability', ''))

        # Генерируем slug
        slug = self._generate_unique_slug(title, article)

        # Получаем список изображений из JSON
        image_urls = row.get('images', [])
        if isinstance(image_urls, str):
            image_urls = [image_urls.strip()] if image_urls.strip() else []

        # Проверяем существование товара по НАЗВАНИЮ (title)
        product = None
        try:
            product = Product.objects.get(title=title)

            if self.update_existing:
                # Обновляем существующий товар
                product.article = article
                product.description = description
                product.details = details
                product.category = category
                product.availability = availability
                product.is_active = True

                # Сбрасываем изображения при обновлении
                if self.update_existing:
                    product.preview_image.delete(save=False)
                    product.images.all().delete()

                product.save()
                self.updated_count += 1
            else:
                self.warnings.append(
                    f"Строка {row_num}: Товар '{title}' уже существует, пропущен")
                self.skipped_count += 1
                return True

        except Product.DoesNotExist:
            product = None

        # Если товара нет - создаем новый
        if not product:
            product = Product(
                title=title,
                article=article,
                slug=slug,
                description=description,
                details=details,
                category=category,
                availability=availability,
                is_active=True
            )
            # Мы сохраним изображения позже, после создания объекта
            product.save()
            self.imported_count += 1

        # Обработка изображений
        self._download_and_save_images(product, image_urls)

        return True

    def _download_and_save_images(self, product, image_urls):
        """Скачивание и сохранение изображений для товара"""
        if not image_urls:
            return

        # Проверяем, не был ли отменен импорт перед скачиванием изображений
        if IMPORT_PROGRESS.get('cancelled', False):
            return

        first_image_url = image_urls[0]
        other_image_urls = image_urls[1:]

        # Скачиваем и сохраняем preview_image
        try:
            # Проверяем отмену перед каждым скачиванием
            if IMPORT_PROGRESS.get('cancelled', False):
                return

            preview_img_file = self._download_image_file(first_image_url)
            if preview_img_file:
                product.preview_image.save(
                    preview_img_file.name, preview_img_file, save=True)
        except Exception as e:
            self.warnings.append(
                f"Не удалось загрузить preview для {product.title}: {str(e)}")

        # Скачиваем и сохраняем остальные изображения
        for idx, img_url in enumerate(other_image_urls):
            # Проверяем отмену перед каждым скачиванием
            if IMPORT_PROGRESS.get('cancelled', False):
                return

            try:
                img_file = self._download_image_file(img_url)
                if img_file:
                    # Генерируем alt-текст для изображения
                    # +2 потому что первое изображение - preview (индекс 1)
                    image_index = idx + 2
                    alt_text = f"{product.title} - изображение {image_index}"

                    ProductImage.objects.create(
                        product=product,
                        image=img_file,
                        order=idx + 1,
                        alt=alt_text
                    )
            except Exception as e:
                self.warnings.append(
                    f"Не удалось загрузить изображение для {product.title}: {str(e)}")

    def _download_image_file(self, image_url):
        """Скачивает изображение по URL и возвращает InMemoryUploadedFile"""
        try:
            # Используем глобальную сессию для повторного использования соединений
            # Уменьшаем timeout до 3 секунд для быстрой реакции
            response = SESSION.get(image_url, timeout=3, stream=True)

            if response.status_code == 200:
                # Извлекаем имя файла из URL
                parsed_url = urlparse(image_url)
                original_filename = os.path.basename(parsed_url.path)
                if not original_filename or '.' not in original_filename:
                    # Если не получилось извлечь имя файла, используем дефолтное
                    content_type = response.headers.get(
                        'content-type', 'image/jpeg')
                    ext = 'jpg'
                    if 'png' in content_type:
                        ext = 'png'
                    elif 'gif' in content_type:
                        ext = 'gif'
                    original_filename = f'image.{ext}'

                # Читаем содержимое
                content = response.content

                # Создаем BytesIO объект из содержимого
                img_io = io.BytesIO(content)

                # Получаем Content-Type из заголовков
                content_type = response.headers.get(
                    'content-type', 'image/jpeg')

                # Создаем InMemoryUploadedFile
                img_file = InMemoryUploadedFile(
                    img_io,          # файлоподобный объект
                    # field_name (не используется при ручном создании)
                    None,
                    original_filename,
                    content_type,    # тип контента
                    len(content),    # размер
                    None             # charset (не используется)
                )
                return img_file
        except requests.exceptions.Timeout:
            # Не выводим сообщения о тайм-аутах, чтобы не засорять логи
            pass
        except requests.exceptions.RequestException:
            # Не выводим сообщения об ошибках сети для каждого изображения
            pass
        except Exception:
            # Не выводим сообщения об исключениях для каждого изображения
            pass
        return None

    def _parse_details(self, details_str):
        """Парсинг характеристик из HTML строки"""
        if not details_str:
            return {}

        details_dict = {}
        details_str = str(details_str).strip()

        # Разбиваем по разделителю |
        parts = details_str.split('|')

        for part in parts:
            part = part.strip()
            if ':' in part:
                # Удаляем HTML теги
                part = re.sub(r'<[^>]+>', '', part)
                key, value = part.split(':', 1)
                details_dict[key.strip()] = value.strip()

        return details_dict

    def _parse_availability(self, availability_str):
        """Парсинг статуса наличия"""
        if not availability_str:
            return 'in_stock'

        availability_str = str(availability_str).lower()

        if 'в наличии' in availability_str or 'наличие' in availability_str:
            return 'in_stock'
        elif 'под заказ' in availability_str or 'заказ' in availability_str:
            return 'order'

        return 'in_stock'

    def _generate_unique_slug(self, title, article=''):
        """Генерация уникального slug"""
        # Транслитерация для русских символов
        translit_dict = {
            'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e',
            'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
            'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
            'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
            'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya'
        }

        # Если есть артикул - используем его
        if article:
            base_slug = article.lower()
        else:
            # Транслитерация названия
            title_lower = title.lower()
            base_slug = ''.join(translit_dict.get(c, c) for c in title_lower)

        # Очищаем от недопустимых символов
        base_slug = re.sub(r'[^\w\s-]', '', base_slug)
        base_slug = re.sub(r'[-\s]+', '-', base_slug).strip('-')

        # Проверяем уникальность
        slug = base_slug
        counter = 1
        while Product.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        return slug

    def _update_progress(self):
        """Обновление прогресса импорта"""
        global IMPORT_PROGRESS

        # Проверяем, не был ли отменен импорт
        if IMPORT_PROGRESS.get('cancelled', False):
            raise InterruptedError("Импорт был отменен пользователем")

        # Рассчитываем прогресс только по количеству обработанных товаров
        if self.total_rows > 0:
            percentage = int((self.processed_rows / self.total_rows) * 100)
            # Ограничиваем процент от 0 до 100
            percentage = max(0, min(100, percentage))
        else:
            percentage = 0

        IMPORT_PROGRESS['processed'] = self.processed_rows
        IMPORT_PROGRESS['total'] = self.total_rows
        IMPORT_PROGRESS['percentage'] = percentage

        # Вызываем callback функцию для обновления прогресса, если установлена
        if self.progress_callback:
            self.progress_callback(self.processed_rows, self.total_rows)

    def _process_additional_images(self, product, url_str):
        """Обработка дополнительных изображений из поля url"""
        if not url_str:
            return

        url_str = str(url_str).strip()

        # Если это уже есть в preview_image, не дублируем
        if product.preview_image and url_str == product.preview_image:
            return

        # Удаляем существующие дополнительные изображения при обновлении
        if self.update_existing:
            product.images.all().delete()

        # Создаем дополнительное изображение
        try:
            ProductImage.objects.create(
                product=product,
                image=url_str,
                order=1
            )
        except Exception as e:
            self.warnings.append(
                f"Не удалось добавить изображение для товара {product.title}: {str(e)}")

    def get_result_message(self):
        """Возвращает сообщение о результате импорта"""
        messages = []

        if self.imported_count > 0:
            messages.append(
                f"[СОЗДАНО] Импортировано: {self.imported_count} товаров")

        if self.updated_count > 0:
            messages.append(
                f"[ОБНОВЛЕНО] Обновлено: {self.updated_count} товаров")

        if self.skipped_count > 0:
            messages.append(
                f"[ПРОПУЩЕНО] Пропущено: {self.skipped_count} товаров")

        if self.warnings:
            messages.append(
                f"\n[ПРЕДУПРЕЖДЕНИЕ] Предупреждения ({len(self.warnings)}):")
            messages.extend(
                [f"  • {w}" for w in self.warnings[:5]])  # Первые 5
            if len(self.warnings) > 5:
                messages.append(
                    f"  ... и еще {len(self.warnings) - 5} предупреждений")

        if self.errors:
            messages.append(f"\n[ОШИБКА] Ошибки ({len(self.errors)}):")
            messages.extend([f"  • {e}" for e in self.errors[:5]])  # Первые 5
            if len(self.errors) > 5:
                messages.append(f"  ... и еще {len(self.errors) - 5} ошибок")

        return '\n'.join(messages) if messages else "Нет данных для отображения"
# import csv
# import json
# import pandas as pd
# from io import BytesIO, StringIO
# from django.core.files.uploadedfile import InMemoryUploadedFile
# from .models import Product, Category


# class ImportProcessor:
#     def __init__(self, file, update_existing=False, delete_missing=False):
#         self.file = file
#         self.update_existing = update_existing
#         self.delete_missing = delete_missing
#         self.errors = []
#         self.warnings = []
#         self.imported_count = 0
#         self.updated_count = 0
#         self.skipped_count = 0

#     def process_file(self):
#         """Определяет формат файла и запускает соответствующий обработчик"""
#         file_extension = self.file.name.split('.')[-1].lower()

#         if file_extension == 'csv':
#             return self._process_csv()
#         elif file_extension in ['xlsx', 'xls']:
#             return self._process_excel()
#         elif file_extension == 'json':
#             return self._process_json()
#         else:
#             self.errors.append(
#                 f"Неподдерживаемый формат файла: {file_extension}")
#             return False

#     def _process_csv(self):
#         """Обработка CSV файла"""
#         try:
#             # Читаем файл в текстовом режиме
#             if hasattr(self.file, 'read'):
#                 content = self.file.read()
#                 if isinstance(content, bytes):
#                     content = content.decode('utf-8')
#                 csv_file = StringIO(content)
#             else:
#                 csv_file = self.file

#             reader = csv.DictReader(csv_file)
#             return self._process_data_rows(reader)
#         except Exception as e:
#             self.errors.append(f"Ошибка при чтении CSV файла: {str(e)}")
#             return False

#     def _process_excel(self):
#         """Обработка Excel файла"""
#         try:
#             # Читаем файл
#             if hasattr(self.file, 'read'):
#                 content = self.file.read()
#                 df = pd.read_excel(BytesIO(content))
#             else:
#                 df = pd.read_excel(self.file)

#             # Конвертируем DataFrame в список словарей
#             data = df.to_dict('records')
#             return self._process_data_rows(data)
#         except Exception as e:
#             self.errors.append(f"Ошибка при чтении Excel файла: {str(e)}")
#             return False

#     def _process_json(self):
#         """Обработка JSON файла"""
#         try:
#             # Читаем файл
#             if hasattr(self.file, 'read'):
#                 content = self.file.read()
#                 if isinstance(content, bytes):
#                     content = content.decode('utf-8')
#                 data = json.loads(content)
#             else:
#                 data = json.load(self.file)

#             # Если это один объект, оборачиваем в список
#             if isinstance(data, dict):
#                 data = [data]

#             return self._process_data_rows(data)
#         except Exception as e:
#             self.errors.append(f"Ошибка при чтении JSON файла: {str(e)}")
#             return False

#     def _process_data_rows(self, rows):
#         """Обработка строк данных"""
#         try:
#             # Сохраняем список существующих артикулов для проверки
#             existing_articles = set(
#                 Product.objects.values_list('article', flat=True))
#             processed_articles = set()

#             # start=2 для учета заголовка
#             for row_num, row in enumerate(rows, start=2):
#                 try:
#                     result = self._process_single_row(row)
#                     if result and row.get('article'):
#                         processed_articles.add(row['article'])
#                 except Exception as e:
#                     self.errors.append(f"Ошибка в строке {row_num}: {str(e)}")
#                     continue

#             # Удаляем отсутствующие товары если нужно
#             if self.delete_missing:
#                 missing_articles = existing_articles - processed_articles
#                 deleted_count = Product.objects.filter(
#                     article__in=missing_articles).delete()[0]
#                 self.warnings.append(
#                     f"Удалено {deleted_count} отсутствующих товаров")

#             return len(self.errors) == 0

#         except Exception as e:
#             self.errors.append(f"Ошибка при обработке данных: {str(e)}")
#             return False

#     def _process_single_row(self, row):
#         """Обработка одной строки данных"""
#         # Валидация обязательных полей
#         if not row.get('title'):
#             self.errors.append("Отсутствует название товара")
#             return False

#         # Получаем или создаем категорию
#         category = None
#         if row.get('category'):
#             try:
#                 category, created = Category.objects.get_or_create(
#                     name=row['category'],
#                     defaults={'slug': self._generate_slug(row['category'])}
#                 )
#                 if created:
#                     self.warnings.append(
#                         f"Создана новая категория: {row['category']}")
#             except Exception as e:
#                 self.errors.append(
#                     f"Ошибка при обработке категории '{row.get('category')}': {str(e)}")
#                 return False

#         # Проверяем существование товара
#         try:
#             product = Product.objects.get(article=row['article'])

#             if self.update_existing:
#                 # Обновляем существующий товар
#                 product.title = row['title']
#                 product.description = row.get('description', '')
#                 product.price = self._parse_price(row.get('price', 0))
#                 if category:
#                     product.category = category
#                 product.is_active = self._parse_boolean(
#                     row.get('is_active', True))

#                 # Обработка preview_image
#                 if row.get('preview_image'):
#                     product.preview_image = row['preview_image']
#                 elif row.get('images'):
#                     product.preview_image = row['images']

#                 product.save()
#                 self.updated_count += 1
#             else:
#                 self.warnings.append(
#                     f"Товар с артикулом {row['article']} уже существует, пропущен")
#                 self.skipped_count += 1

#         except Product.DoesNotExist:
#             # Создаем новый товар
#             product = Product.objects.create(
#                 title=row['title'],
#                 article=row.get('article', ''),
#                 description=row.get('description', ''),
#                 price=self._parse_price(row.get('price', 0)),
#                 category=category,
#                 is_active=True,  # Все импортированные товары активны
#                 preview_image=row.get(
#                     'preview_image', '') or row.get('images', ''),
#                 details=row.get('details', {})
#             )
#             self.imported_count += 1

#         # Обработка дополнительных изображений
#         if row.get('additional_images'):
#             self._process_additional_images(product, row['additional_images'])
#         elif row.get('url'):
#             # Если есть поле url, используем его как дополнительное изображение
#             self._process_additional_images(product, row['url'])

#         return True

#     def _parse_price(self, price_value):
#         """Парсинг цены"""
#         try:
#             if isinstance(price_value, str):
#                 # Удаляем все символы кроме цифр и точки
#                 price_value = ''.join(
#                     c for c in price_value if c.isdigit() or c == '.' or c == ',')
#                 # Заменяем запятую на точку
#                 price_value = price_value.replace(',', '.')
#             return float(price_value) if price_value else 0
#         except:
#             return 0

#     def _parse_boolean(self, value):
#         """Парсинг булевых значений"""
#         if isinstance(value, bool):
#             return value
#         if isinstance(value, str):
#             return value.lower() in ['true', '1', 'yes', 'да', 'вкл', 'on']
#         return bool(value)

#     def _generate_slug(self, name):
#         """Генерация slug из названия"""
#         import re
#         # Транслитерация и очистка
#         slug = re.sub(r'[^\w\s-]', '', name.lower())
#         slug = re.sub(r'[-\s]+', '-', slug)
#         return slug.strip('-')

#     def _process_additional_images(self, product, images_str):
#         """Обработка дополнительных изображений"""
#         from .models import ProductImage

#         if not images_str:
#             return

#         # Разделяем изображения по запятой или точке с запятой
#         image_urls = [url.strip() for url in images_str.replace(
#             ';', ',').split(',') if url.strip()]

#         # Удаляем существующие изображения если обновляем
#         if self.update_existing:
#             product.images.all().delete()

#         # Создаем новые изображения
#         for order, image_url in enumerate(image_urls, start=1):
#             if image_url:
#                 ProductImage.objects.create(
#                     product=product,
#                     image=image_url,
#                     order=order
#                 )

#     def get_result_message(self):
#         """Возвращает сообщение о результате импорта"""
#         messages = []

#         if self.imported_count > 0:
#             messages.append(f"Импортировано: {self.imported_count} товаров")

#         if self.updated_count > 0:
#             messages.append(f"Обновлено: {self.updated_count} товаров")

#         if self.skipped_count > 0:
#             messages.append(f"Пропущено: {self.skipped_count} товаров")

#         if self.warnings:
#             messages.extend([f"Предупреждение: {w}" for w in self.warnings])

#         if self.errors:
#             messages.extend([f"Ошибка: {e}" for e in self.errors])

#         return '\n'.join(messages) if messages else "Нет данных для отображения"
