from django.test import TestCase
from .models import Product, Category,Review
from django.contrib.auth.models import User
from django.urls import reverse
from .forms import ReviewForm

class CategoryModelTests(TestCase):

    def test_category_str_method(self):
        category = Category.objects.create(name="Test Category")
        self.assertEqual(str(category), "Test Category")
    
    def test_product_str_method(self):
        external_id = Product.objects.create(
            category=Category.objects.create(name="Test Category"),
            external_id="12345",
            name="Test Product",
            description="This is a test product.",
            price=19.99,
            stock_quantity=10
        )

        self.assertEqual(str(external_id), "Test Product")


    def test_review_str_method(self):
        review = Review.objects.create(
            product=Product.objects.create(
                category=Category.objects.create(name="Test Category"),
                external_id="12345",
                name="Test Product",
                description="This is a test product.",
                price=19.99,
                stock_quantity=10
            ),
            user= User.objects.create_user(username="Test User", password="testpass"),
            rating=5,
            comment="This is a test review."
        )
        self.assertEqual(str(review), "Test User - Test Product - 5 stars")

    def test_homepage_status_code(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core_app/home.html")

    def test_product_list_status_code(self):
        response = self.client.get(reverse('store_app:product_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "store_app/product_list.html")

    def setUp(self):
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.product = Product.objects.create(
            category=self.category,
            name='Test Product',
            price=10.00
        )

    def test_product_detail_status_code(self):
        url = reverse('store_app:product_detail', args=[1])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "store_app/product_detail.html")

    def test_urls_status(self):
        urls = (
            reverse('store_app:category_list'),
            reverse('store_app:product_list'),
            reverse('store_app:product_detail', args=[1])
        )
        self.assertEqual(urls, ('/store/kategoriler/', '/store/products/', '/store/products/1/'))

    def test_review_form_valid(self):
        form_data = {
            'product': Product.objects.create(
                category=Category.objects.create(name="Test Category"),
                external_id="12345",
                name="Test Product",
                description="This is a test product.",
                price=19.99,
                stock_quantity=10
            ),
            'user': User.objects.create_user(username="Test User", password="testpass"),
            'rating': 5,
            'comment': "This is a test review."
        }
        form = ReviewForm(data=form_data)
        self.assertTrue(form.is_valid())