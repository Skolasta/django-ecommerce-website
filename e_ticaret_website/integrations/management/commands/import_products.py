import requests
from django.core.management.base import BaseCommand, CommandError
from store_app.models import Product, Category
from django.conf import settings

# Manual product import
class Command(BaseCommand):
    API_URL = settings.DUMMY_JSON_API_URL  # URL from .env file

    # Get products from API
    def handle(self, *args, **kwargs):
        self.stdout.write('Fetching products from API...')

        try:
            response = requests.get(self.API_URL)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            raise CommandError(f"Error during API request: {e}")

        # Exchange rate information
        try:
            self.stdout.write('Fetching current USD/TRY exchange rate...')
            api_key = settings.EXCHANGE_RATE_API_KEY # API key from .env file
            rate_url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/USD"
            rate_response = requests.get(rate_url)
            rate_response.raise_for_status()
            rate_data = rate_response.json()
            usd_to_try_rate = rate_data['conversion_rates']['TRY']
            self.stdout.write(self.style.SUCCESS(f"Current rate: 1 USD = {usd_to_try_rate} TRY"))
        except requests.exceptions.RequestException as e:
            raise CommandError(f"Error during exchange rate API request: {e}")
        except KeyError:
            raise CommandError("Could not find 'conversion_rates' or 'TRY' key in exchange rate API response.")
        

        # We loop over data['products']
        for product_data in data['products']:
            try:
                category_name = product_data['category']
                category, created = Category.objects.get_or_create(
                    name=category_name,
                    defaults={'slug': category_name.lower().replace(' ', '-')}
                )
                price_in_usd = product_data['price']
                price_in_try = round(price_in_usd * usd_to_try_rate, 2)
                
                product, created = Product.objects.update_or_create(
                    external_id=product_data['id'],
                    defaults={
                        'category': category,
                        'name': product_data['title'],
                        'description': product_data['description'],
                        'price': price_in_try, # We now save the TRY price to the database
                        'image_url': product_data['thumbnail'],
                        'stock_quantity': product_data.get('stock', 0),
                    }
                )

                if created:
                    self.stdout.write(self.style.SUCCESS(f"New product created: '{product.name}'"))
                else:
                    self.stdout.write(f"Product updated: '{product.name}'")
            except KeyError as e:
                # If a key we expect (e.g., 'category' or 'title') is missing in the incoming data, log this error and continue
                self.stdout.write(self.style.ERROR(f"Product with ID {product_data.get('id')} has a missing key: {e}. Skipping this product."))


        self.stdout.write(self.style.SUCCESS('All products successfully fetched and database updated!'))
