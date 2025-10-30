from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from .models import Category, Product


class CategoryListView(ListView):
    model = Category
    template_name = 'catalog/category_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        return Category.objects.filter(parent=None, is_active=True).order_by('order')


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
