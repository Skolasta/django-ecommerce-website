from django.db import models
from django.urls import reverse
from django.conf import settings


# Create your models here.
# Order model
class Order(models.Model):
    # Order status choices
    STATUS_CHOICES = [
        ('pending', 'Ödeme Bekleniyor'),
        ('processing', 'Hazırlanıyor'),
        ('shipped', 'Kargolandı'),
        ('delivered', 'Teslim Edildi'),
        ('cancelled', 'İptal Edildi'),
    ]
    # Order information
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    shipping_address = models.CharField(max_length=255)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(choices=STATUS_CHOICES, max_length=20, default='processing')
    cart_snapshot = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

    def get_absolute_url(self):
        return reverse('order_detail', args=[str(self.id)])

# Order item model
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE , related_name='items')
    product = models.ForeignKey('store_app.Product', on_delete=models.CASCADE, related_name='order_items')
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order {self.order.id}"
