from django.core.management.base import BaseCommand
from django.core.files import File
from apps.catalog.utils import ImportProcessor


class Command(BaseCommand):
    help = 'Import products from archive CSV file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            help='Path to the CSV file to import',
            default='imports/arhive_models.csv'
        )
        parser.add_argument(
            '--update-existing',
            action='store_true',
            help='Update existing products',
        )
        parser.add_argument(
            '--delete-missing',
            action='store_true',
            help='Delete products not in the file',
        )

    def handle(self, *args, **options):
        file_path = options['file']
        update_existing = options['update_existing']
        delete_missing = options['delete_missing']

        try:
            # Открываем файл
            with open(file_path, 'rb') as f:
                file_obj = File(f)
                file_obj.name = file_path.split('/')[-1]

                self.stdout.write(f'Importing from {file_path}...')

                # Создаем процессор импорта
                processor = ImportProcessor(
                    file_obj, update_existing, delete_missing)

                # Обрабатываем файл
                success = processor.process_file()

                if success:
                    self.stdout.write(
                        self.style.SUCCESS('Import completed successfully!')
                    )
                    self.stdout.write(
                        f'Imported: {processor.imported_count} products')
                    self.stdout.write(
                        f'Updated: {processor.updated_count} products')
                    self.stdout.write(
                        f'Skipped: {processor.skipped_count} products')

                    if processor.warnings:
                        self.stdout.write(self.style.WARNING('Warnings:'))
                        for warning in processor.warnings:
                            self.stdout.write(f'  - {warning}')

                else:
                    self.stdout.write(
                        self.style.ERROR('Import failed!')
                    )
                    if processor.errors:
                        self.stdout.write(self.style.ERROR('Errors:'))
                        for error in processor.errors:
                            self.stdout.write(f'  - {error}')

        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(f'File not found: {file_path}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error: {str(e)}')
            )
