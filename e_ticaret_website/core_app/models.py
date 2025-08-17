from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator 


# Create your models here.
# User profile model
class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    location = models.CharField(max_length=100, blank=True, null=False) 
    birth_date = models.DateField(null=True, blank=True)
    phone_regex = RegexValidator(
    regex=r'^\d{11}$',
    message="Telefon numarası '05xxxxxxxxx' formatında, 11 haneli ve sadece sayılardan oluşmalıdır."
)
    phone_number = models.CharField(validators=[phone_regex], max_length=11, blank=True)
    


    def __str__(self):
        return self.user.username
    
