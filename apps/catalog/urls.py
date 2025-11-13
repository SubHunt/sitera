from django.urls import path, re_path
from . import views
from .admin_views import import_products, import_preview, download_import_template

app_name = 'catalog'

urlpatterns = [
    path('', views.CategoryListView.as_view(), name='category_list'),
    re_path(r'^category/(?P<slug>[-a-zA-Z0-9_а-яёА-ЯЁ]+)/$',
            views.CategoryDetailView.as_view(), name='category'),
    re_path(r'^product/(?P<slug>[-a-zA-Z0-9_а-яёА-ЯЁ]+)/$',
            views.ProductDetailView.as_view(), name='product'),
    path('api/search/', views.search_products, name='search_products'),

    # Import URLs
    path('import/', import_products, name='import_products'),
    path('import/preview/', import_preview, name='import_preview'),
    path('import/template/', download_import_template,
         name='download_import_template'),
    path('import/progress/', views.import_progress, name='import_progress'),
    path('import/cancel/', views.cancel_import, name='cancel_import'),
]
