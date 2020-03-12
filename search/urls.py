from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.my_register, name='register'),
    path('creator/', views.creator, name='creator'),
    path('post/', views.post, name='post'),
    path('changepass/', views.change_pass, name='change_pass'),
    path('blog/<int:num>/', views.blog, name='blog'),
    path('blog/<int:blog>/<int:com_remv>/', views.com_remove, name='com_remove'),
    path('postremove/<int:post_id>/', views.post_remove, name='post_remove'),
    path('editblog/<int:blogedit>/', views.edit_blog, name='edit_blog'),
    path('editcom/<int:comedit>/', views.edit_com, name='edit_com'),
    path('status/<int:change_status>/', views.status, name='status'),
]