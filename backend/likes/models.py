from django.db import models

class Like(models.Model):
    from_who = models.ForeignKey("users.User", related_name= "from_user", on_delete= models.CASCADE)
    to_post = models.ForeignKey("posts.Post", related_name= "to_post", on_delete= models.CASCADE )
    created_at = models.DateTimeField(auto_now_add= True)

