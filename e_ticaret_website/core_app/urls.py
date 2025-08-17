from django.urls import path
from . import views
from django.contrib.auth.views import LoginView, LogoutView,PasswordChangeView ,PasswordChangeDoneView
from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views

app_name = 'core_app'

urlpatterns = [
    path('', views.home, name='home'),
    path('hakkimizda/', views.hakkimizda, name='hakkimizda'),

    # Auth URL'leri
    path('login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('signup/', views.SignUpView.as_view(), name='signup'),

    # Profil ve Hesap URL'leri
    path('profil/kurulum/', views.ProfileSetupView.as_view(), name='profile_setup'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-of-use/', views.terms_of_use, name='terms_of_use'),
    path('profilim', views.account_dashboard_view, name='account_dashboard'),
    path('profilim/guncelle/', views.account_update_view, name='profile_edit'),

    #Şifre değiştirme URL' leri
    path('hesabim/sifre-degistir/', PasswordChangeView.as_view(template_name='core_app/password_change_form.html', success_url=reverse_lazy('core_app:password_change_done')), name='password_change'), 
    path('sifre-degistir/basarili/',auth_views.PasswordChangeDoneView.as_view(template_name='core_app/password_change_done.html'),name='password_change_done'),   
]