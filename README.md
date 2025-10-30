# Sitera - B2G Сайт профессионального оборудования

**Проект:** B2G-сайт для продажи профессионального оборудования синхронного перевода, аудио/видео и конференц-медиа под госзакупки (44-ФЗ, 223-ФЗ)

**Технологии:** Django 5.2.7 + Python 3.13 + TailwindCSS + PostgreSQL

## 📋 Описание проекта

Sitera - это специализированный B2G-портал для продажи профессионального оборудования:
- Системы синхронного перевода
- Системы отображения информации (видеостены)
- Видеоконференцсвязь
- Аудио/видео оборудование для конференц-залов

Проект ориентирован на работу с государственными и корпоративными заказчиками, с возможностью формирования коммерческих предложений и участия в тендерах.

## 🚀 Ключевые возможности

- **Каталог товаров** с фильтрацией по категориям и характеристикам
- **Детальные страницы товаров** с галереей изображений и техническими характеристиками
- **Форма запроса коммерческого предложения** для каждого товара
- **Административная панель** с возможностью импорта товаров из CSV/JSON/XML/XLSX
- **Адаптивный дизайн** для всех устройств
- **Поиск по каталогу** с подсветкой результатов

## 🛠️ Технологический стек

### Backend:
- **Django 5.2.7** - веб-фреймворк
- **PostgreSQL** - база данных
- **Python 3.13** - язык программирования
- **python-decouple** - управление переменными окружения
- **django-crispy-forms** - стилизация форм
- **crispy-bootstrap5** - Bootstrap 5 интеграция

### Frontend:
- **TailwindCSS** - CSS фреймворк
- **Bootstrap 5** - UI компоненты
- **JavaScript** - интерактивность

### Development:
- **django-debug-toolbar** - отладочная панель
- **django-extensions** - дополнительные утилиты Django

## 📁 Структура проекта

```
sitera/
├── config/                    # настройки проекта
│   ├── settings/
│   │   ├── base.py           # общие настройки
│   │   ├── development.py    # для разработки
│   │   └── production.py     # для продакшена
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── apps/
│   ├── catalog/              # каталог товаров
│   ├── contacts/             # формы обратной связи
│   └── core/                 # общие компоненты
├── static/                   # статические файлы
├── templates/                # шаблоны
├── media/                    # загруженные файлы
├── requirements/             # зависимости
├── manage.py
└── README.md
```

## 🚀 Установка и запуск проекта

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd sitera
```

### 2. Создание и активация виртуального окружения

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Настройка переменных окружения

Скопируйте файл примера и настройте переменные:

```bash
cp .env.example .env
```

Отредактируйте `.env` файл:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DB_NAME=sitera_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 5. Настройка базы данных PostgreSQL

Создайте базу данных:

```sql
CREATE DATABASE sitera_db;
CREATE USER sitera_user WITH PASSWORD 'your-password';
GRANT ALL PRIVILEGES ON DATABASE sitera_db TO sitera_user;
```

### 6. Применение миграций

```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Создание суперпользователя

Используйте кастомную команду для создания администратора:

```bash
python manage.py create-admin-user
```

Эта команда создаст суперпользователя с логином `admin` и паролем `admin`. Если пользователь уже существует, команда пропустит создание.

### 8. Сборка статических файлов

```bash
python manage.py collectstatic
```

### 9. Запуск сервера разработки

```bash
python manage.py runserver
```

Проект будет доступен по адресу: http://127.0.0.1:8000

Административная панель: http://127.0.0.1:8000/admin

## 🎨 Работа с фронтендом

Для компиляции TailwindCSS:

```bash
# Установка Node.js зависимостей (если еще не установлены)
npm install

# Компиляция CSS в режиме разработки
npm run dev

# Компиляция CSS для продакшена
npm run build
```

## 📝 Доступные команды управления

### Стандартные команды Django:
- `python manage.py runserver` - запуск сервера разработки
- `python manage.py migrate` - применение миграций
- `python manage.py createsuperuser` - создание суперпользователя
- `python manage.py collectstatic` - сборка статических файлов

### Кастомные команды:
- `python manage.py create-admin-user` - создание администратора с логином/паролем admin

## 🔧 Разработка

### Структура приложений:

- **catalog** - модели товаров, категорий, изображений
- **contacts** - формы обратной связи и запросы КП
- **core** - общие утилиты и компоненты

### Модели данных:

- **Category** - категории товаров (с поддержкой вложенности)
- **Product** - товары с характеристиками и изображениями
- **ProductImage** - дополнительные изображения товаров
- **ContactRequest** - запросы коммерческих предложений

## 📦 Деплой

Для продакшен-развертывания используйте:

```bash
# Установка продакшен-зависимостей
pip install -r requirements/production.txt

# Настройка переменных окружения для продакшена
# (DEBUG=False, настройка ALLOWED_HOSTS, etc.)

# Сборка статических файлов
python manage.py collectstatic --noinput

# Применение миграций
python manage.py migrate
```

## 🤝 Contributing

1. Fork проекта
2. Создайте feature-branch (`git checkout -b feature/AmazingFeature`)
3. Commit ваши изменения (`git commit -m 'Add some AmazingFeature'`)
4. Push в branch (`git push origin feature/AmazingFeature`)
5. Откройте Pull Request

## 📄 Лицензия

Этот проект распространяется под лицензией MIT. Подробности в файле LICENSE.

## 📞 Контакты

При возникновении вопросов или предложений, пожалуйста, свяжитесь с командой разработки.