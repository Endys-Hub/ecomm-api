from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE) 
    fullname = models.CharField(max_length=50)
    phone = models.CharField(max_length=50)
    gender = models.CharField(max_length=50)
    image = models.ImageField(upload_to='profile', default='https://cdn-icons-png.flaticon.com/128/456/456212.png')
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.fullname
