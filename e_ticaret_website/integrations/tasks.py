import os
import requests
from store_app.models import Product, Category
from celery import shared_task
from django.conf import settings
from django.shortcuts import redirect

# Bu görev, DummyJSON API üzerinden ürünleri çeker ve veritabanını günceller.
@shared_task #Celery için
def update_products_task():
    API_URL = settings.DUMMY_JSON_API_URL  # .env dosyasından alınan URL

    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"API isteği sırasında hata oluştu: {e}")
        return 

    #Kur bilgileri
    try:
        api_key = settings.EXCHANGE_RATE_API_KEY
        rate_url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/USD"
        rate_response = requests.get(rate_url)
        rate_response.raise_for_status()
        rate_data = rate_response.json()
        usd_to_try_rate = rate_data['conversion_rates']['TRY']
    except Exception as e:
        return redirect('store_app:product_list', exception=f"Kur bilgisi alınamadı: {e}")

    # Ürün verilerini işleme
    product_count = 0
    for product_data in data.get('products', []): 
        try:
            category_name = product_data['category']
            category, _ = Category.objects.get_or_create(
                name=category_name,
                defaults={'slug': category_name.lower().replace(' ', '-')}
            )

            price_in_usd = product_data['price']
            price_in_try = round(price_in_usd * usd_to_try_rate, 2)

            _, created = Product.objects.update_or_create(
                external_id=product_data['id'],
                defaults={
                    'category': category,
                    'name': product_data['title'],
                    'description': product_data['description'],
                    'price': price_in_try,
                    'image_url': product_data['thumbnail'],
                    'stock_quantity': product_data.get('stock', 0),
                }
            )
            product_count += 1

        except KeyError as e:
            print(f"ID {product_data.get('id')} olan üründe eksik anahtar: {e}. Bu ürün atlanıyor.")

    print(f"İşlem tamamlandı. {product_count} ürün başarıyla veritabanına eklendi/güncellendi.")
    return f"{product_count} adet ürün işlendi."