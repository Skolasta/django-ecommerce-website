from .models import Order, OrderItem
from django import forms

# Order creation form
class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'shipping_address', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Adınız'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Soyadınız'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'E-posta Adresiniz'}),
            'shipping_address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teslimat Adresiniz'}),
        }

# Order update form
class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'shipping_address', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Adınız'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Soyadınız'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'E-posta Adresiniz'}),
            'shipping_address': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Teslimat Adresiniz', 'rows': 3}),
        }