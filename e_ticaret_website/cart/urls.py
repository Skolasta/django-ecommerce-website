from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    # Sepete ürün ekleme
    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),
    # Sepetten ürün kaldırma
    path('remove_from_cart/', views.remove_from_cart, name='remove_from_cart'),
    path('view_cart/', views.view_cart, name='view_cart'),
]