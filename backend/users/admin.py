from django.contrib import admin

from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import User


# Register your models here.
@admin.register(User)
class UsersAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "username", "avatar", "created_at")
    list_display_links = ("name", "username")
    search_fields = ("name", "username")
    readonly_fields = ("created_at",)

    def get_photo(self, obj):
        if obj.photo:
            return mark_safe(f'<img src="{obj.photo.url}" width="100">')
        return "-"


admin.site.index_title = "Панелька"
admin.site.site_header = "Админка"
