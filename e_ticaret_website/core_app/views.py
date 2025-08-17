from django.shortcuts import render, redirect
from . import models
from store_app.models import Product
from django.views.generic import CreateView
from django.urls import reverse_lazy
from . forms import RegisterForm,UserProfileForm
from django.contrib.auth import login
from django.views.generic import UpdateView
from django.contrib.auth.decorators import login_required
from .models import UserProfile
from .forms import UserUpdateForm, UserProfileForm
from django.contrib import messages 


# Create your views here.
# Home page
def home(request):
     latest_products = Product.objects.order_by('-created_at')[:12]
     context = {
          'latest_products': latest_products
     }
     return render(request, 'core_app/home.html', context)

# About us page
def hakkimizda(request):
    return render(request, 'core_app/hakkımızda.html')

# Registration form view
class SignUpView(CreateView):
    form_class = RegisterForm 
    template_name = 'registration/signup.html'

    def form_valid(self, form):
        user = form.save() 
        login(self.request, user)
        return redirect('core_app:profile_setup') 

# Profile setup view
class ProfileSetupView(UpdateView):
    model = models.UserProfile
    form_class = UserProfileForm
    template_name = 'core_app/profile_setup.html'
    success_url = reverse_lazy('core_app:home')

    def get_object(self, queryset=None):
        return self.request.user.userprofile
    
# Privacy Policy and Terms of Use
def privacy_policy(request):
    return render(request, 'core_app/privacy_policy.html')

def terms_of_use(request):
    return render(request, 'core_app/terms_of_use.html')


@login_required # If the user is logged in
def account_dashboard_view(request):
    # Get user profile information
    try:
        profile = request.user.userprofile
        context = {
            'user': request.user,
            'profile': profile, 
        }
        return render(request, 'core_app/account_dashboard.html', context)

    except UserProfile.DoesNotExist:
        return redirect('core_app:profile_setup')

# User profile update view
@login_required
def account_update_view(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, instance=request.user.userprofile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('core_app:account_dashboard')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = UserProfileForm(instance=request.user.userprofile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    return render(request, 'core_app/profile_edit.html', context)
