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
            update_existing = form.cleaned_data['update_existing']
            delete_missing = form.cleaned_data['delete_missing']

            # Создаем процессор импорта
            processor = ImportProcessor(file, update_existing, delete_missing)

            # Обрабатываем файл
            success = processor.process_file()

            if success:
                messages.success(request, 'Импорт успешно завершен!')
                messages.info(request, processor.get_result_message())
            else:
                messages.error(request, 'Ошибка при импорте товаров')
                for error in processor.errors:
                    messages.error(request, error)

            # Если это AJAX запрос, возвращаем JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': success,
                    'message': processor.get_result_message(),
                    'imported': processor.imported_count,
                    'updated': processor.updated_count,
                    'skipped': processor.skipped_count,
                    'errors': processor.errors,
                    'warnings': processor.warnings
                })

            return redirect('admin:catalog_product_changelist')
    else:
        form = ImportForm()

    return render(request, 'admin/catalog/import_products.html', {
        'form': form,
        'title': 'Импорт товаров',
        'opts': {'app_label': 'catalog', 'model_name': 'Product'},
        'has_change_permission': True,
    })


@staff_member_required
def import_preview(request):
    """Предпросмотр данных перед импортом"""
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        update_existing = request.POST.get('update_existing') == 'on'
        delete_missing = request.POST.get('delete_missing') == 'on'

        # Создаем процессор для предпросмотра
        processor = ImportProcessor(file, update_existing, delete_missing)

        # Получаем первые несколько строк для предпросмотра
        try:
            file_extension = file.name.split('.')[-1].lower()
            preview_data = []

            if file_extension == 'csv':
                import csv
                from io import StringIO
                content = file.read().decode('utf-8')
                csv_file = StringIO(content)
                reader = csv.DictReader(csv_file)
                preview_data = list(reader)[:5]  # Первые 5 строк

            elif file_extension in ['xlsx', 'xls']:
                import pandas as pd
                from io import BytesIO
                df = pd.read_excel(BytesIO(file.read()))
                preview_data = df.head(5).to_dict('records')

            elif file_extension == 'json':
                import json
                content = file.read().decode('utf-8')
                data = json.loads(content)
                if isinstance(data, dict):
                    data = [data]
                preview_data = data[:5]

            return JsonResponse({
                'success': True,
                'preview': preview_data,
                'total_rows': len(preview_data)
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
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="import_template.csv"'

    writer = csv.writer(response)
    writer.writerow(['title', 'article', 'description',
                    'price', 'category', 'is_active'])

    # Добавляем пример данных
    writer.writerow([
        'Пример товара', 'ART-001', 'Описание товара', '10000.50', 'Название категории', 'True'
    ])

    return response
