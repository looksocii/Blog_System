from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.my_register, name='register'),
    path('login/', views.my_login, name='login'),
    path('logout/', views.my_logout, name='logout'),
    path('blog/<int:num>/', views.blog, name='blog'),
    path('blog/<int:blog>/<int:com_remv>', views.com_remove, name='com_remove'),
    path('profile/', views.profile, name='profile'),
    path('post/', views.post, name='post'),
    path('editblog/<int:num_blogedit>/', views.edit_blog, name='edit_blog'),
    path('editcom/<int:num_comedit>/', views.edit_com, name='edit_com'),
]