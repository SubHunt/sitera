from django.core.management.base import BaseCommand
from django.db import connection
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from decouple import config


class Command(BaseCommand):
    help = 'Создание базы данных PostgreSQL'

    def handle(self, *args, **options):
        # Параметры подключения к PostgreSQL (без указания базы данных)
        db_settings = {
            'host': config('DB_HOST', default='localhost'),
            'port': config('DB_PORT', default='5432'),
            'user': config('DB_USER', default='postgres'),
            'password': config('DB_PASSWORD', default=''),
        }

        db_name = config('DB_NAME', default='sitera_db')

        try:
            # Подключаемся к PostgreSQL (к системной базе данных postgres)
            conn = psycopg2.connect(
                host=db_settings['host'],
                port=db_settings['port'],
                user=db_settings['user'],
                password=db_settings['password'],
                database='postgres'  # Системная база данных
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()

            # Проверяем существует ли база данных
            cursor.execute(
                f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
            exists = cursor.fetchone()

            if exists:
                self.stdout.write(self.style.WARNING(
                    f'База данных {db_name} уже существует'))
            else:
                # Создаем базу данных
                cursor.execute(f'CREATE DATABASE {db_name}')
                self.stdout.write(self.style.SUCCESS(
                    f'База данных {db_name} успешно создана'))

            cursor.close()
            conn.close()

        except psycopg2.OperationalError as e:
            self.stdout.write(self.style.ERROR(
                f'Ошибка подключения к PostgreSQL: {e}'))
            self.stdout.write(self.style.WARNING(
                'Убедитесь что PostgreSQL сервер запущен и доступен'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка: {e}'))
