from django.urls import path
from . import views

app_name = 'store_app'

urlpatterns = [
    # Ürün listeleme
    path('products/', views.product_list, name='product_list'),
    # Ürün detay
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),
    # Arama
    path('search/', views.search_results, name='search'),
    # Sepet
    path('sepet/', views.sepet, name='sepet'),  
    #Kategoriler
    path('kategoriler/', views.category_list, name='category_list'),
    path('kategori/<slug:category_slug>/', views.products_by_category, name='products_by_category'),
]
