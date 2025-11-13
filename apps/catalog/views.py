from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.admin.views.decorators import staff_member_required
from .models import Category, Product


class CategoryListView(ListView):
    model = Category
    template_name = 'catalog/category_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        return Category.objects.filter(parent=None, is_active=True).order_by('order').prefetch_related('children', 'products')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем статистику
        context['total_categories'] = Category.objects.filter(
            is_active=True).count()
        context['total_products'] = Product.objects.filter(
            is_active=True).count()
        return context


class CategoryDetailView(DetailView):
    model = Category
    template_name = 'catalog/category_detail.html'
    context_object_name = 'category'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.get_object()

        # Получаем товары из этой категории и подкатегорий
        products = Product.objects.filter(
            category=category,
            is_active=True
        ).select_related('category').prefetch_related('images')

        context['products'] = products
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = 'catalog/product_detail.html'
    context_object_name = 'product'
    slug_url_kwarg = 'slug'

    def get_object(self):
        product = super().get_object()
        # Увеличиваем счетчик просмотров
        product.views_count += 1
        product.save(update_fields=['views_count'])
        return product

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()

        # Получаем похожие товары из той же подкатегории
        if product.subcategory:
            similar_products = Product.objects.filter(
                subcategory=product.subcategory,
                is_active=True
            ).exclude(id=product.id)[:4]
        else:
            similar_products = Product.objects.filter(
                category=product.category,
                is_active=True
            ).exclude(id=product.id)[:4]

        context['similar_products'] = similar_products
        context['images'] = product.images.all().order_by('order')
        return context


def search_products(request):
    """
    API эндпоинт для поиска товаров
    """
    query = request.GET.get('q', '').strip()

    if not query or len(query) < 2:
        return JsonResponse({'products': []})

    # Ищем товары по названию, артикулу и описанию
    products = Product.objects.filter(
        Q(title__icontains=query) |
        Q(article__icontains=query) |
        Q(description__icontains=query) |
        Q(category__name__icontains=query),
        is_active=True
        # Ограничиваем до 10 результатов
    ).select_related('category').prefetch_related('images')[:10]

    products_data = []
    for product in products:
        product_data = {
            'id': product.id,
            'title': product.title,
            'url': product.get_absolute_url(),
            'category': product.category.name,
            'article': product.article,
            'description': product.description[:100] + '...' if len(product.description) > 100 else product.description,
        }

        # Добавляем изображение если есть
        if product.preview_image:
            product_data['image'] = product.preview_image.url
        elif product.images.first():
            product_data['image'] = product.images.first().image.url
        else:
            product_data['image'] = None

        products_data.append(product_data)

    return JsonResponse({'products': products_data})


def import_progress(request):
    """
    API эндпоинт для получения прогресса импорта
    """
    from .utils import IMPORT_PROGRESS
    return JsonResponse(IMPORT_PROGRESS)


@staff_member_required
def cancel_import(request):
    """Отмена импорта товаров"""
    if request.method == 'POST':
        from .utils import IMPORT_PROGRESS
        IMPORT_PROGRESS['cancelled'] = True
        return JsonResponse({'status': 'success', 'message': 'Импорт отменен'})
    return JsonResponse({'status': 'error', 'message': 'Метод не разрешен'}, status=405)
