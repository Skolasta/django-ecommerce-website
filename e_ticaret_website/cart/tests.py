from django.test import TestCase
from . import views,urls,context_processors
from django.urls import reverse
from django.test import Client
from django.contrib.auth.models import User
from store_app.models import Product,Category
from django.urls import resolve
from django.test import RequestFactory


class TestViews(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        self.category = Category.objects.create(name='Test Category', slug = 'test-category')
        self.product = Product.objects.create(name='Test Product', price=10.0, description='Test Description', image_url='test.jpg',category = self.category)
        self.cart = self.client.session.get('cart', {})

    # Sepete ürün ekleme
    def test_add_to_cart(self):
        response = self.client.post(reverse('cart:add_to_cart'), {'product_id': self.product.id})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('cart:view_cart'))

    #Sepet görünümü
    def test_view_cart(self):
        response = self.client.get(reverse('cart:view_cart'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cart/cart_detail.html')
    
    #Sepetten ürün silme
    def test_remove_from_cart(self):
        self.client.post(reverse('cart:add_to_cart'), {'product_id': self.product.id})
        response = self.client.post(reverse('cart:remove_from_cart'), {'product_id': self.product.id})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('cart:view_cart'))

    def test_checkout(self):
        #Sepete ürün ekledikten sonra kontrol ediyoruz.
        self.client.post(reverse('cart:add_to_cart'), {'product_id': self.product.id})
        #Sepeti onayladık
        response = self.client.get(reverse('orders:checkout'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orders/checkout.html')

class TestUrls(TestCase):

    def test_add_to_cart_url(self):
        url = reverse('cart:add_to_cart')
        self.assertEqual(resolve(url).func, views.add_to_cart)

    def test_view_cart_url(self):
        url = reverse('cart:view_cart')
        self.assertEqual(resolve(url).func, views.view_cart)
    
    def test_remove_from_cart_url(self):
        url = reverse('cart:remove_from_cart')
        self.assertEqual(resolve(url).func, views.remove_from_cart)

class TestContextProcessors(TestCase):

    # Cart total testi
    def test_cart_total(self):
        factory = RequestFactory()
        request = factory.get(reverse('cart:view_cart'))
        request.session = self.client.session
        context = context_processors.cart_context(request)
        self.assertIn('total_cart_items', context)
        self.assertIn('cart_item_count', context)
        self.assertIn('all_categories', context)
