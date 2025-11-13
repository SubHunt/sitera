from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .forms import ImportForm
from .utils import ImportProcessor


@staff_member_required
def import_products(request):
    """Представление для импорта товаров"""
    if request.method == 'POST':
        form = ImportForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            category = form.cleaned_data.get('category')
            update_existing = form.cleaned_data['update_existing']
            delete_missing = form.cleaned_data['delete_missing']

            # Проверяем, является ли это AJAX запросом
            is_ajax = (
                request.headers.get('X-Requested-With') == 'XMLHttpRequest' or
                request.POST.get('ajax') == 'true'
            )

            try:
                # Создаем процессор импорта
                category_id = category.id if category else None
                processor = ImportProcessor(
                    file, category_id, update_existing, delete_missing)

                # Для AJAX запросов устанавливаем callback для отслеживания прогресса
                if is_ajax:
                    def progress_callback(processed, total):
                        # Callback ничего не делает, так как прогресс хранится в глобальной переменной
                        pass

                    processor.set_progress_callback(progress_callback)

                # Обрабатываем файл
                success = processor.process_file()

                result = {
                    'success': success,
                    'message': processor.get_result_message(),
                    'imported': processor.imported_count,
                    'updated': processor.updated_count,
                    'skipped': processor.skipped_count,
                    'errors': processor.errors,
                    'warnings': processor.warnings
                }

                if is_ajax:
                    # Для AJAX запросов возвращаем JSON
                    return JsonResponse(result)
                else:
                    # Для обычных запросов используем Django messages
                    if success:
                        messages.success(request, 'Импорт успешно завершен!')
                        # Форматируем сообщение с результатами
                        result_lines = processor.get_result_message().split('\n')
                        for line in result_lines:
                            if line.startswith('[СОЗДАНО]') or line.startswith('✅'):
                                messages.success(request, line)
                            elif line.startswith('[ОБНОВЛЕНО]') or line.startswith('🔄'):
                                messages.info(request, line)
                            elif line.startswith('[ПРОПУЩЕНО]') or line.startswith('⏭️'):
                                messages.warning(request, line)
                            elif line.startswith('[ПРЕДУПРЕЖДЕНИЕ]') or line.startswith('⚠️'):
                                messages.warning(request, line)
                            elif line.startswith('[ОШИБКА]') or line.startswith('❌'):
                                messages.error(request, line)
                    else:
                        messages.error(request, 'Ошибка при импорте товаров')
                        result_lines = processor.get_result_message().split('\n')
                        for line in result_lines:
                            if line.strip():
                                messages.error(request, line)

                    return redirect('admin:catalog_product_changelist')
            except Exception as e:
                error_result = {
                    'success': False,
                    'message': f'Ошибка при обработке импорта: {str(e)}',
                    'errors': [str(e)],
                    'imported': 0,
                    'updated': 0,
                    'skipped': 0,
                    'warnings': []
                }

                if is_ajax:
                    return JsonResponse(error_result)
                else:
                    messages.error(
                        request, f'Ошибка при обработке импорта: {str(e)}')
                    return redirect('admin:catalog_product_changelist')
    else:
        form = ImportForm()

    return render(request, 'admin/catalog/import_products.html', {
        'form': form,
        'title': 'Импорт товаров',
        'opts': {'app_label': 'catalog', 'model_name': 'Product'},
        'has_change_permission': True,
        # Добавляем ссылку на наш CSS
        'media': '<link href="/static/css/admin.css" rel="stylesheet">',
    })


@staff_member_required
def import_preview(request):
    """Предпросмотр данных перед импортом"""
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']

        try:
            file_extension = file.name.split('.')[-1].lower()
            preview_data = []

            if file_extension == 'csv':
                import csv
                from io import StringIO
                content = file.read().decode('utf-8')
                csv_file = StringIO(content)
                reader = csv.DictReader(csv_file)
                preview_data = list(reader)[:10]  # Первые 10 строк

            elif file_extension in ['xlsx', 'xls']:
                import pandas as pd
                from io import BytesIO
                df = pd.read_excel(BytesIO(file.read()))
                preview_data = df.head(10).to_dict('records')

            elif file_extension == 'json':
                import json
                content = file.read().decode('utf-8')
                data = json.loads(content)
                if isinstance(data, dict):
                    data = [data]
                preview_data = data[:10]

            return JsonResponse({
                'success': True,
                'preview': preview_data,
                'total_rows': len(preview_data),
                'columns': list(preview_data[0].keys()) if preview_data else []
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

    return JsonResponse({'success': False, 'error': 'Файл не предоставлен'})


@staff_member_required
def download_import_template(request):
    """Скачивание шаблона для импорта"""
    import csv
    from django.http import HttpResponse

    # Создаем шаблон CSV
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="import_template.csv"'

    # Добавляем BOM для корректного отображения в Excel
    response.write('\ufeff')

    writer = csv.writer(response)

    # Заголовки из вашего CSV
    writer.writerow([
        'title', 'article', 'category', 'price', 'availability',
        'description', 'details', 'images', 'url'
    ])

    # Добавляем пример данных
    writer.writerow([
        'Пример товара',
        'ART-001',
        'Архивные модели',
        '0',
        'Наличие:В наличии',
        'Описание товара с детальной информацией',
        'Производитель: Digital Projection | Наименование: <h3>ART-001</h3> | Партномер: <h3>ART-001</h3>',
        'https://example.com/image.jpg',
        'https://example.com/product/art-001/'
    ])

    return response
