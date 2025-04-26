from django.db import models

class User(models.Model):
    first_name = models.CharField(max_length= 30, verbose_name= '')
    user_name = models.CharField(max_length= 30 , verbose_name= '')
    avatar = models.ImageField(upload_to= 'photo', null = True, blank= True , verbose_name= '')
    created_at = models.DateTimeField(auto_now_add= True , verbose_name= '')
