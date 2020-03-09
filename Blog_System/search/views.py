from builtins import object
from datetime import datetime
from fnmatch import filter

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Group, User
from django.shortcuts import *

from blogger.models import Comment, Post


# Create your views here.
def index(request):
    context = dict()
    if request.method == 'POST':
        blog_name = request.POST.get('blog')

        if request.user.is_superuser:
            post_all = Post.objects.filter(
                title__icontains=blog_name
            )
        else:
            post_all = Post.objects.filter(
                title__icontains=blog_name,
                status=True
            )

        context['post_all'] = post_all
        context['sign_page'] = "sign_page"
        context['login_page'] = "login_page"
        return render(request, 'search/index.html', context)

    if request.user.is_superuser:
        post_all = Post.objects.all()
    else:
        post_all = Post.objects.filter(status=True)
    
    context['post_all'] = post_all
    context['sign_page'] = "sign_page"
    context['login_page'] = "login_page"
    return render(request, 'search/index.html', context)

def my_register(request):
    context = dict()
    if request.method == 'POST':
        user = User.objects.create_user(
            username=request.POST.get('username'),
            password=request.POST.get('password'),
            first_name=request.POST.get('first_name'),
            last_name=request.POST.get('last_name'),
            email=request.POST.get('email')
        )
        group = Group.objects.get(name='audience')
        user.groups.add(group)
        user.save()

        context['login_page'] = "login_page"
        return render(request, 'search/login.html', context)

    context['sign_page'] = "sign_page"
    return render(request, 'search/signup.html', context)

def my_login(request):
    context = dict()
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('index')
        else:
            context['username'] = username
            context['password'] = password
            context['error'] = "ชื่อผู้ใช้ หรือ รหัสผ่าน ไม่ถูกต้อง"
            context['user'] = "This is index User."
            return render(request, 'search/login.html', context)
    
    context['login_page'] = "login_page"
    return render(request, 'search/login.html', context)

@login_required
def my_logout(request):
    logout(request)
    return redirect('login')

def profile(request):
    context = dict()
    context['sign_page'] = "sign_page"
    context['login_page'] = "login_page"
    return render(request, 'search/profile.html', context)

def blog(request, num):
    context = dict()
    if request.method == 'POST':
        com = Comment(
            content=request.POST.get('content'),
            create_time=datetime.now(),
            user_id_id=request.user.id,
            post_id_id=num
        )
        com.save()
        blog = Post.objects.get(pk=num)
        com = Comment.objects.filter(post_id_id=num)
        context['blog'] = blog
        context['com'] = com
        return render(request, 'search/blog.html', context)

    blog = Post.objects.get(pk=num)
    com = Comment.objects.filter(post_id_id=num)
    context['blog'] = blog
    context['com'] = com
    context['sign_page'] = "sign_page"
    context['login_page'] = "login_page"
    return render(request, 'search/blog.html', context)

@login_required
@permission_required('blogger.change_post')
def edit_blog(request, num_blogedit):
    context = dict()
    if request.method == 'POST':
        status = request.POST.get('checkbox')
        if status == "Show":
            status = True
        else:
            status = False

        blog = Post.objects.get(pk=num_blogedit)
        blog.title = request.POST.get('title')
        blog.content = request.POST.get('content')
        blog.update_time = datetime.now()
        blog.status = status
        blog.save()
        context['blog'] = blog
        return render(request, 'search/blog.html', context)
    
    blog = Post.objects.get(pk=num_blogedit)
    context['blog'] = blog
    return render(request, 'search/edit_blog.html', context)

@login_required
@permission_required('blogger.add_post', 'login/')
def post(request):
    context = dict()
    if request.method == 'POST':
        status = request.POST.get('checkbox')
        if status == "Show":
            status = True
        else:
            status = False

        post = Post(
            user_id_id=1,
            title=request.POST.get('title'),
            content=request.POST.get('content'),
            create_time=datetime.now(),
            update_time = datetime.now(),
            status=status,
        )
        post.save()
        context['blog'] = post
        return render(request, 'search/blog.html', context)

    return render(request, 'search/post.html', context)

@login_required
def edit_com(request, num_comedit):
    context = dict()
    if request.method == 'POST':
        com_new = Comment.objects.get(pk=num_comedit)
        com_new.content = request.POST.get('content')
        com_new.save()
        blog = Post.objects.get(pk=com_new.post_id.id)
        com = Comment.objects.filter(post_id_id=com_new.post_id.id)
        context['blog'] = blog
        context['com'] = com
        return render(request, 'search/blog.html', context)

    com = Comment.objects.get(pk=num_comedit)
    context['com'] = com
    return render(request, 'search/edit_com.html', context)

def com_remove(request, blog, com_remv):
    context = dict()
    com = Comment.objects.get(pk=com_remv)
    com.delete()

    blog = Post.objects.get(pk=blog)
    all_com = Comment.objects.filter(post_id_id=blog)
    context['blog'] = blog
    context['com'] = all_com
    context['sign_page'] = "sign_page"
    context['login_page'] = "login_page"
    return render(request, 'search/blog.html', context)
