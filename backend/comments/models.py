from django.db import models



# class Comment(models.Model):
#     post_id = models.ForeignKey('Post', on_delete= models.CASCADE, related_name= "comments")
#     file = models.FileField(blank=True, null=True)
#     title = models.CharField(max_length=200, blank=True)
#     text = models.TextField(max_length=200000, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     likes_number = models.IntegerField(default=0)