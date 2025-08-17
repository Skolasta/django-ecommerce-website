from django.contrib import admin
from .models import Order, OrderItem

# Register your models here.
# Admin registration
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product'] 
    extra = 1

# Add products from Order
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'created_at', 'paid_amount']
    list_filter = ['status', 'created_at']
    inlines = [OrderItemInline]
