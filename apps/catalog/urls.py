from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.CategoryListView.as_view(), name='category_list'),
    path('category/<slug:slug>/',
         views.CategoryDetailView.as_view(), name='category'),
    path('product/<slug:slug>/', views.ProductDetailView.as_view(), name='product'),
    path('api/search/', views.search_products, name='search_products'),
]
