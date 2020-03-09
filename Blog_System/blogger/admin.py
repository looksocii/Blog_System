from webbrowser import register
from django.contrib import admin
from .models import Post, Comment
from django.contrib.auth.models import Permission

# Register your models here.

admin.site.register(Post)

admin.site.register(Comment)

admin.site.register(Permission)
