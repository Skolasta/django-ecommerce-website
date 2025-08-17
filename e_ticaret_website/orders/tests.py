from django.test import TestCase
from .models import Order, OrderItem
from django.contrib.auth.models import User
from decimal import Decimal
from store_app.models import Category, Product
from django.utils import timezone
from django.urls import reverse

# Create your tests here.
class OrdersTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Test Category')
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.order = Order.objects.create(
            user=self.user,
            paid_amount=Decimal('100.00'),
            first_name='Test',
            last_name='Test',
            email='test@example.com',
            created_at=timezone.now(),
            status='Pending'
        )

        self.product = Product.objects.create(
            name='Test Product',
            price=Decimal('50.00'),
            category=self.category,
            stock_quantity=10,
            description='Test Product Description'
        )
        
        self.order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=2,
            price=Decimal('50.00')
        )

    def test_order_creation(self):
        self.assertEqual(self.order.user, self.user)
        self.assertEqual(self.order.paid_amount, Decimal('100.00'))
        self.assertEqual(self.order.first_name, 'Test')
        self.assertEqual(self.order.last_name, 'Test')
        self.assertEqual(self.order.email, 'test@example.com')
        self.assertEqual(self.order.created_at.date(), timezone.now().date())
        self.assertEqual(self.order.status, 'Pending')

    def test_order_item_creation(self):
        self.assertEqual(self.order_item.order, self.order)
        self.assertEqual(self.order_item.product, self.product)
        self.assertEqual(self.order_item.quantity, 2)
        self.assertEqual(self.order_item.price, Decimal('50.00'))

    def test_url_status(self):
        urls = (
            reverse('orders:order_list'),
            reverse('orders:checkout', args=()),
            reverse('orders:orders_success', args=[self.order.id]),
        )
        self.assertEqual(urls, ('/orders/', '/orders/checkout/', '/orders/success/1/'))
    
    def test_checkout_view_requires_cart(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('orders:checkout'))
        self.assertEqual(response.status_code, 302)
