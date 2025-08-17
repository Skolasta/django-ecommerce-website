from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile

# Kayıt formu
class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        label="E-posta Adresi", 
        required=True
    )
    # E-posta adresinin benzersiz olduğunu kontrol et
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Bu e-posta adresi zaten kullanılıyor.")
        return email
    # Şifrelerin eşleşip eşleşmediğini kontrol et
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            self.add_error("password2", "Şifreler eşleşmiyor.")
    # Meta bilgileri
    class Meta:
        model = User
        fields = ('first_name', 'last_name','username','email') 
        labels = {
            'username': 'Kullanıcı Adı',
            'first_name': 'Ad',
            'last_name': 'Soyad',
            'email': 'E-posta Adresi',
        }

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        
        self.fields['password2'].label = "Şifre (Tekrar)"

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label

# Kullanıcı profili formu 2
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('phone_number', 'location', 'birth_date')
        labels = {
            'phone_number': 'Telefon Numarası',
            'location': 'Şehir',
            'birth_date': 'Doğum Tarihi',
        }
        widgets = {
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Telefon Numaranızı '}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Şehir'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Doğum Tarihi', 'type': 'date'}),
        }

# Kullanıcı güncelleme formu
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile

# Registration form
class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        label="E-posta Adresi", 
        required=True
    )
    # Check if email address is unique
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already in use.")
        return email
    # Check if passwords match
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            self.add_error("password2", "Passwords do not match.")
    # Meta information
    class Meta:
        model = User
        fields = ('first_name', 'last_name','username','email') 
        labels = {
            'username': 'Kullanıcı Adı',
            'first_name': 'Ad',
            'last_name': 'Soyad',
            'email': 'E-posta Adresi',
        }

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        
        self.fields['password2'].label = "Şifre (Tekrar)"

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label

# User profile form 2
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('phone_number', 'location', 'birth_date')
        labels = {
            'phone_number': 'Telefon Numarası',
            'location': 'Şehir',
            'birth_date': 'Doğum Tarihi',
        }
        widgets = {
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Telefon Numaranızı '}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Şehir'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Doğum Tarihi', 'type': 'date'}),
        }

# User update form
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')
        labels = {
            'first_name': 'Ad',
            'last_name': 'Soyad',
            'email': 'E-posta Adresi',
        }
