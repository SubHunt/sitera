# Sitera.kz - Сайт каталога продукции

Django-проект для каталога продукции компании Sitera.

## Развертывание

**ОСНОВНАЯ ИНСТРУКЦИЯ ПО РАЗВЕРТЫВАНИЮ:** [`DEPLOYMENT.md`](DEPLOYMENT.md)

### Краткое описание развертывания:

1. **Локальная подготовка:**
   ```bash
   venv\Scripts\activate.bat
   python manage.py create_all_categories
   python manage.py import_archive_products --file imports/arhive_models.csv
   python scripts/export_database.py
   tar -czf media_backup.tar.gz media/
   ```

2. **Подключение к серверу:**
   ```bash
   ssh root@77.246.247.122
   ```

3. **Развертывание:**
   ```bash
   cd /var/www/
   git clone https://github.com/SubHunt/sitera sitera
   cd sitera
   docker-compose -f docker-compose.prod.yml up -d --build
   ```

4. **Проверка:**
   - Сайт: http://77.246.247.122
   - Админка: http://77.246.247.122/admin

## Структура проекта

- `apps/` - Django приложения
- `config/` - Настройки Django
- `static/` - Статические файлы
- `templates/` - Шаблоны
- `media/` - Медиафайлы (изображения товаров и категорий)
- `nginx/` - Конфигурация Nginx
- `scripts/` - Вспомогательные скрипты

## Основные команды

### Локальная разработка:
```bash
# Запуск сервера разработки
python manage.py runserver

# Создание категорий
python manage.py create_all_categories

# Импорт товаров
python manage.py import_archive_products --file imports/arhive_models.csv

# Создание суперпользователя
python manage.py createsuperuser
```

### Продакшн (на сервере):
```bash
# Перезапуск сервисов
docker-compose -f docker-compose.prod.yml restart

# Просмотр логов
docker-compose -f docker-compose.prod.yml logs -f

# Выполнение миграций
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate --noinput

# Сбор статических файлов
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --no-input --clear
```

## Важные файлы

- `.env.prod` - Переменные окружения для продакшена
- `docker-compose.prod.yml` - Docker конфигурация для продакшена
- `nginx/nginx.conf` - Конфигурация Nginx
- `gunicorn.conf.py` - Настройки Gunicorn

## Резервное копирование

Автоматическое резервное копирование настраивается через cron:
```bash
# Ежедневный бэкап в 3:00
0 3 * * * /var/www/sitera/scripts/backup.sh
```

## Поддержка

При возникновении проблем:
1. Проверьте логи: `docker-compose -f docker-compose.prod.yml logs -f`
2. Перезапустите сервисы: `docker-compose -f docker-compose.prod.yml restart`
3. Смотрите полную инструкцию в [`DEPLOYMENT.md`](DEPLOYMENT.md)