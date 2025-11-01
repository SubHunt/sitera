import csv
import json
import pandas as pd
from io import BytesIO, StringIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from .models import Product, Category


class ImportProcessor:
    def __init__(self, file, update_existing=False, delete_missing=False):
        self.file = file
        self.update_existing = update_existing
        self.delete_missing = delete_missing
        self.errors = []
        self.warnings = []
        self.imported_count = 0
        self.updated_count = 0
        self.skipped_count = 0

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

            # Если это один объект, оборачиваем в список
            if isinstance(data, dict):
                data = [data]

            return self._process_data_rows(data)
        except Exception as e:
            self.errors.append(f"Ошибка при чтении JSON файла: {str(e)}")
            return False

    def _process_data_rows(self, rows):
        """Обработка строк данных"""
        try:
            # Сохраняем список существующих артикулов для проверки
            existing_articles = set(
                Product.objects.values_list('article', flat=True))
            processed_articles = set()

            # start=2 для учета заголовка
            for row_num, row in enumerate(rows, start=2):
                try:
                    result = self._process_single_row(row)
                    if result and row.get('article'):
                        processed_articles.add(row['article'])
                except Exception as e:
                    self.errors.append(f"Ошибка в строке {row_num}: {str(e)}")
                    continue

            # Удаляем отсутствующие товары если нужно
            if self.delete_missing:
                missing_articles = existing_articles - processed_articles
                deleted_count = Product.objects.filter(
                    article__in=missing_articles).delete()[0]
                self.warnings.append(
                    f"Удалено {deleted_count} отсутствующих товаров")

            return len(self.errors) == 0

        except Exception as e:
            self.errors.append(f"Ошибка при обработке данных: {str(e)}")
            return False

    def _process_single_row(self, row):
        """Обработка одной строки данных"""
        # Валидация обязательных полей
        if not row.get('title'):
            self.errors.append("Отсутствует название товара")
            return False

        if not row.get('article'):
            self.errors.append("Отсутствует артикул товара")
            return False

        # Получаем или создаем категорию
        category = None
        if row.get('category'):
            try:
                category, created = Category.objects.get_or_create(
                    name=row['category'],
                    defaults={'slug': self._generate_slug(row['category'])}
                )
                if created:
                    self.warnings.append(
                        f"Создана новая категория: {row['category']}")
            except Exception as e:
                self.errors.append(
                    f"Ошибка при обработке категории '{row.get('category')}': {str(e)}")
                return False

        # Проверяем существование товара
        try:
            product = Product.objects.get(article=row['article'])

            if self.update_existing:
                # Обновляем существующий товар
                product.title = row['title']
                product.description = row.get('description', '')
                product.price = self._parse_price(row.get('price', 0))
                if category:
                    product.category = category
                product.is_active = self._parse_boolean(
                    row.get('is_active', True))
                product.save()
                self.updated_count += 1
            else:
                self.warnings.append(
                    f"Товар с артикулом {row['article']} уже существует, пропущен")
                self.skipped_count += 1

        except Product.DoesNotExist:
            # Создаем новый товар
            product = Product.objects.create(
                title=row['title'],
                article=row['article'],
                description=row.get('description', ''),
                price=self._parse_price(row.get('price', 0)),
                category=category,
                is_active=self._parse_boolean(row.get('is_active', True))
            )
            self.imported_count += 1

        return True

    def _parse_price(self, price_value):
        """Парсинг цены"""
        try:
            if isinstance(price_value, str):
                # Удаляем все символы кроме цифр и точки
                price_value = ''.join(
                    c for c in price_value if c.isdigit() or c == '.' or c == ',')
                # Заменяем запятую на точку
                price_value = price_value.replace(',', '.')
            return float(price_value) if price_value else 0
        except:
            return 0

    def _parse_boolean(self, value):
        """Парсинг булевых значений"""
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ['true', '1', 'yes', 'да', 'вкл', 'on']
        return bool(value)

    def _generate_slug(self, name):
        """Генерация slug из названия"""
        import re
        # Транслитерация и очистка
        slug = re.sub(r'[^\w\s-]', '', name.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug.strip('-')

    def get_result_message(self):
        """Возвращает сообщение о результате импорта"""
        messages = []

        if self.imported_count > 0:
            messages.append(f"Импортировано: {self.imported_count} товаров")

        if self.updated_count > 0:
            messages.append(f"Обновлено: {self.updated_count} товаров")

        if self.skipped_count > 0:
            messages.append(f"Пропущено: {self.skipped_count} товаров")

        if self.warnings:
            messages.extend([f"Предупреждение: {w}" for w in self.warnings])

        if self.errors:
            messages.extend([f"Ошибка: {e}" for e in self.errors])

        return '\n'.join(messages) if messages else "Нет данных для отображения"
