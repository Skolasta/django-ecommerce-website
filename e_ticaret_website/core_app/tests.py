from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from datetime import date
from .models import UserProfile
from . import forms


class UserProfileModelTests(TestCase):
    #Userprofili için test sınıfı
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.user_profile = UserProfile.objects.get(user=self.user)
        
    def test_user_profile_auto_creation(self):
        #Test sinyali ile oluştur
        new_user = User.objects.create_user(
            username='newuser',
            email='newuser@example.com',
            password='testpass123'
        )
        
        # Signal tarafından otomatik profil oluşturuldu mu kontrol et
        self.assertTrue(UserProfile.objects.filter(user=new_user).exists())
        profile = UserProfile.objects.get(user=new_user)
        self.assertEqual(str(profile), 'newuser')

    def test_user_profile_update(self):
        # Mevcut profili güncelle
        self.user_profile.birth_date = date(1990, 1, 1)
        self.user_profile.phone_number = '05234567890'
        self.user_profile.location = 'Ankara'
        self.user_profile.save()

        # Veritabanından tekrar yükle
        self.user_profile.refresh_from_db()
        self.assertEqual(self.user_profile.birth_date, date(1990, 1, 1))
        self.assertEqual(self.user_profile.phone_number, '05234567890')
        self.assertEqual(self.user_profile.location, 'Ankara')


class UserFormsTests(TestCase):
    #Form testleri
    def test_register_form_valid(self):
        form_data = {
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'email': 'newuser@example.com',
            'password1': 'complexpass123',
            'password2': 'complexpass123',
        }
        form = forms.RegisterForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        user = form.save()
        self.assertEqual(user.username, 'newuser')
        self.assertEqual(user.email, 'newuser@example.com')
        self.assertEqual(user.first_name, 'New')
        self.assertEqual(user.last_name, 'User')

    def test_register_form_duplicate_email(self):
        #Duplicate email kontrolü
        User.objects.create_user(
            username='existing',
            email='test@example.com',
            password='testpass123'
        )
        
        form_data = {
            'username': 'newuser',
            'email': 'test@example.com',  # Aynı email
            'password1': 'complexpass123',
            'password2': 'complexpass123',
        }
        form = forms.RegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('Bu e-posta adresi zaten kullanılıyor.', form.errors['email'])

    def test_register_form_password_mismatch(self):
        #Şifre uyumsuzluğu testi
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'complexpass123',
            'password2': 'differentpass123',
        }
        form = forms.RegisterForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_user_profile_form_valid(self):
        # Profil formu testi
        user = User.objects.create_user(username='formtestuser', password='testpass123')
        user_profile = UserProfile.objects.get(user=user)  
        
        form_data = {
            'birth_date': '2000-01-01',
            'phone_number': '05123456789',
            'location': 'İstanbul'
        }
        form = forms.UserProfileForm(instance=user_profile, data=form_data)
        self.assertTrue(form.is_valid())
        
        saved_profile = form.save()
        self.assertEqual(saved_profile.birth_date, date(2000, 1, 1))
        self.assertEqual(saved_profile.phone_number, '05123456789')
        self.assertEqual(saved_profile.location, 'İstanbul')

    def test_user_profile_form_invalid_phone(self):
        # Geçersiz telefon numarası testi
        user = User.objects.create_user(username='invalidphoneuser', password='testpass123')
        user_profile = UserProfile.objects.get(user=user)  # Signal ile oluşturulan profili al
        
        form_data = {
            'birth_date': '2000-01-01',
            'phone_number': '123456789',  
            'location': 'İstanbul'
        }
        form = forms.UserProfileForm(instance=user_profile, data=form_data)
        self.assertFalse(form.is_valid())


class CoreAppViewTests(TestCase):
    #View testleri
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='viewtestuser',
            email='viewtest@example.com',
            password='testpass123'
        )
        # Signal ile otomatik oluşturulan profili al ve güncelle
        self.user_profile = UserProfile.objects.get(user=self.user)
        self.user_profile.birth_date = date(2000, 1, 1)
        self.user_profile.phone_number = '05123456789'
        self.user_profile.location = 'İstanbul'
        self.user_profile.save()

    def test_homepage_view(self):
        # Ana sayfa testi
        response = self.client.get(reverse('core_app:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Cartify')  # hakkımızda.html'den

    def test_hakkimizda_view(self):
        # Hakkımızda sayfası testi
        response = self.client.get(reverse('core_app:hakkimizda'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Hakkımızda')

    def test_privacy_policy_view(self):
        # Gizlilik politikası testi
        response = self.client.get(reverse('core_app:privacy_policy'))
        self.assertEqual(response.status_code, 200)

    def test_terms_of_use_view(self):
        # Kullanım şartları testi
        response = self.client.get(reverse('core_app:terms_of_use'))
        self.assertEqual(response.status_code, 200)

    def test_login_view(self):
        # Giriş sayfası testi
        response = self.client.get(reverse('core_app:login'))
        self.assertEqual(response.status_code, 200)

    def test_signup_view_get(self):
        # Kayıt sayfası GET testi
        response = self.client.get(reverse('core_app:signup'))
        self.assertEqual(response.status_code, 200)

    def test_signup_view_post_valid(self):
        # Kayıt sayfası POST testi - geçerli veri
        form_data = {
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'email': 'newuser@example.com',
            'password1': 'complexpass123',
            'password2': 'complexpass123',
        }
        response = self.client.post(reverse('core_app:signup'), data=form_data)
        
        # Kullanıcı oluşturuldu mu kontrol et
        self.assertTrue(User.objects.filter(username='newuser').exists())
        
        # Profil kurulum sayfasına yönlendirildi mi kontrol et
        self.assertRedirects(response, reverse('core_app:profile_setup'))

    def test_account_dashboard_view_authenticated(self):
        # Hesap paneli - giriş yapmış kullanıcı
        self.client.login(username='viewtestuser', password='testpass123')
        response = self.client.get(reverse('core_app:account_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'viewtestuser')

    def test_account_dashboard_view_anonymous(self):
        # Hesap paneli - giriş yapmamış kullanıcı
        response = self.client.get(reverse('core_app:account_dashboard'))
        # Login sayfasına yönlendirilmeli
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_profile_edit_view_authenticated(self):
        # Profil düzenleme - giriş yapmış kullanıcı
        self.client.login(username='viewtestuser', password='testpass123')
        response = self.client.get(reverse('core_app:profile_edit'))
        self.assertEqual(response.status_code, 200)

    def test_profile_edit_view_post(self):
        # Profil düzenleme POST testi
        self.client.login(username='viewtestuser', password='testpass123')
        
        form_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'updated@example.com',
            'birth_date': '1995-05-15',
            'phone_number': '05987654321',
            'location': 'Ankara'
        }
        
        response = self.client.post(reverse('core_app:profile_edit'), data=form_data)
        
        # Hesap paneline yönlendirildi mi kontrol et
        self.assertRedirects(response, reverse('core_app:account_dashboard'))
        
        # Kullanıcı bilgileri güncellendi mi kontrol et
        self.user.refresh_from_db()
        self.user_profile.refresh_from_db()
        
        self.assertEqual(self.user.first_name, 'Updated')
        self.assertEqual(self.user.last_name, 'Name')
        self.assertEqual(self.user.email, 'updated@example.com')
        self.assertEqual(self.user_profile.phone_number, '05987654321')
        self.assertEqual(self.user_profile.location, 'Ankara')