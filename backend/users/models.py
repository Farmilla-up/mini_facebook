from django.db import models

class User(models.Model):
    name  = models.CharField(max_length= 30, verbose_name= 'Имя')
    user_name = models.CharField(max_length= 30 , verbose_name= 'Юз')
    avatar = models.ImageField(upload_to= 'photo', null = True, blank= True , verbose_name= 'Ава')
    created_at = models.DateTimeField(auto_now_add= True , verbose_name= 'Когда зареган')
    # В будущем foreignkey на посты


    class Meta :
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.name