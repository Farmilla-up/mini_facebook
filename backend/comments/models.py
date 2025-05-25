from django.db import models


class Comment(models.Model):
    to_post = models.ForeignKey('posts.Post', on_delete= models.CASCADE, related_name= "comments")
    from_who = models.ForeignKey(
        "users.User", related_name="comment_from_user", on_delete=models.CASCADE
    )
    text = models.TextField(max_length=200000, blank=True)
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, related_name="replies", null=True, blank=True, default= None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

