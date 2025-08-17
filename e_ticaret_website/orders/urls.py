from . import views
from django.urls import path, reverse_lazy

app_name = 'orders'

urlpatterns = [
    # Sipariş listesi
    path('', views.order_list, name='order_list'),
    # Ödeme
    path('checkout/', views.checkout_view, name='checkout'),
    # Başarılı ödeme
    path('success/<int:order_id>/', views.orders_success, name='orders_success'),
    # Iyzico geri dönüş
    path('iyzico-callback/', views.iyzico_callback, name='iyzico_callback'),
]
