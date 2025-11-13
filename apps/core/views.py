from django.shortcuts import render
from django.views.generic import TemplateView
from apps.catalog.models import Category, Product


class HomeView(TemplateView):
    template_name = 'pages/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Получаем основные категории для главной страницы
        main_categories = Category.objects.filter(
            parent=None,
            is_active=True
        ).order_by('order')[:3]

        # Для каждой категории получаем несколько товаров
        for category in main_categories:
            category.featured_products = Product.objects.filter(
                category=category,
                is_active=True
            ).order_by('?')[:4]  # Случайные 4 товара

        context['main_categories'] = main_categories

        # Получаем последние добавленные товары
        context['latest_products'] = Product.objects.filter(
            is_active=True
        ).order_by('-created_at')[:6]

        return context
