from django.db import models
from django.db.models import ForeignKey
import uuid
from users.models import User

# Create your models here.
class Post(models.Model):
    post_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner_id = ForeignKey(User,on_delete= models.CASCADE, related_name= 'posts')
    file = models.FileField(blank= True, null=True)
    title = models.CharField(max_length=200, blank= True )
    text = models.TextField(max_length=200000, blank= True)
    created_at = models.DateTimeField(auto_now_add= True)
    updated_at = models.DateTimeField(auto_now= True)
    likes_number = models.IntegerField(default= 0)
    # comments_number =
    #коменты на будущее