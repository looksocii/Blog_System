from builtins import object
from datetime import datetime
from fnmatch import filter
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Group, User
from django.shortcuts import *
from django.db.models import Count
from blogger.models import Comment, Post
from django.core.exceptions import ObjectDoesNotExist


def index(request):
    if request.method == 'POST':
        blog_name = request.POST.get('blog')

        # -------- แสดงเฉพาะบทความที่ไม่ถูกซ่อน ----------
        if request.user.is_superuser:
            # Blogger แสดงทุกบทความ
            post_all = Post.objects.filter(
                title__icontains=blog_name
            )
        else:
            post_all = Post.objects.filter(
                title__icontains=blog_name,
                status=True
            )
        # --------------------------------------------
        
        # -------- นับความคิดเห็นของแต่ละบทความ ----------
        com = Post.objects.annotate(Count('comment'))
        com = com.values_list('id', 'comment__count')
        # --------------------------------------------

        context = {
            'blog_name': "ผลลัพธ์การค้นหา : " + blog_name,
            'post_all': post_all,
            'com': com,
            'sign_page': "sign_page",
            'login_page': "login_page"
        }
        return render(request, 'search/index.html', context)

    # -------- แสดงเฉพาะบทความที่ไม่ถูกซ่อน ----------
    if request.user.is_superuser:
        # Blogger แสดงทุกบทความ
        post_all = Post.objects.all().order_by('id')
    else:
        post_all = Post.objects.filter(status=True).order_by('id')
    # --------------------------------------------

    # -------- นับความคิดเห็นของแต่ละบทความ ----------
    com = Post.objects.annotate(Count('comment'))
    com = com.values_list('id', 'comment__count')
    # --------------------------------------------

    context = {
        'post_all': post_all,
        'com': com,
        'sign_page': "sign_page",
        'login_page': "login_page"
    }
    return render(request, 'search/index.html', context)

def my_register(request):
    if request.method == 'POST':

        # ----------------- สร้าง user ใหม่แล้วนำเข้ากลุ่มผู้ชม ( audience ) -----------------
        try:
            user = User.objects.get(username=request.POST.get('username'))
        except ObjectDoesNotExist:
            user = None
        if user:
            context = {
                'error': "กรุณาตั้ง username ใหม่",
                'sign_page': "sign_page",
                'username': request.POST.get('username'),
                'password': request.POST.get('password'),
                'first_name': request.POST.get('first_name'),
                'last_name': request.POST.get('last_name'),
                'email': request.POST.get('email')
            }
            return render(request, 'search/signup.html', context)
        else:
            user = User.objects.create_user(
                username=request.POST.get('username'),
                password=request.POST.get('password'),
                first_name=request.POST.get('first_name'),
                last_name=request.POST.get('last_name'),
                email=request.POST.get('email')
            )
            group = Group.objects.get(name='audience') # นำเข้ากลุ่ม
            user.groups.add(group)
            user.save()
            return redirect('login')
        # -----------------------------------------------------------------------------

    return render(request, 'search/signup.html', context={'sign_page': "sign_page"})

def my_login(request):
    context = dict()
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # --------------- เช็คว่า username, password มีอยู่ในข้อมูลหรือไม่ ----------------
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            next_url = request.POST.get('next_url')
            if next_url:
                return redirect(next_url)
            else:
                return redirect('index')
        else: # ไม่มีอยู่ในข้อมูล
            context = {
                'username': username,
                'password': password,
                'error': "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้องกรุณากรอกอีกครั้ง",
                'login_page': "login_page"
            }
            return render(request, 'search/login.html', context)
        # -------------------------------------------------------------------------
        

    # -------- เมื่อมีการส่ง request next มา ----------
    next_url = request.GET.get('next')
    if next_url:
        context['next_url'] = next_url
    # --------------------------------------------

    context['login_page'] = "login_page"
    return render(request, 'search/login.html', context)

@login_required
def my_logout(request):
    logout(request)
    return redirect('login')

def creator(request):
    context = {
        'sign_page': "sign_page",
        'login_page': "login_page"
    }
    return render(request, 'search/creator.html', context)

def blog(request, num):
    if request.method == 'POST':

        # ----------------- การแสดงความคิดเห็น -----------------
        com = Comment(
            content=request.POST.get('content'),
            create_time=datetime.now(),
            user_id_id=request.user.id,
            post_id_id=num
        )
        com.save()
        blog = Post.objects.get(pk=num)
        com = Comment.objects.filter(post_id_id=num)
        context = {
            'blog': blog,
            'com': com
        }
        # ----------------------------------------------------

        return render(request, 'search/blog.html', context)

    # ------- ดึงข้อมูลมาจากตัวแปร num เป็น id ของ blog ------
    blog = Post.objects.get(pk=num)
    com = Comment.objects.filter(post_id_id=num)
    # ---------------------------------------------------

    context = {
        'blog': blog,
        'com': com,
        'sign_page': "sign_page",
        'login_page': "login_page"
    }
    return render(request, 'search/blog.html', context)

@login_required
@permission_required('blogger.change_post')
def edit_blog(request, blogedit):
    if request.method == 'POST':

        # ----- รับ request เช็คดูว่าบทความถูกซ่อนหรือไม่ -----
        if request.POST.get('checkbox') == "Hide":
            status = False
        else:
            status = True
        # ----------------------------------------------
        
        # ---------- แก้ไขความคิดเห็น ( อัพเดท ) ----------
        blog = Post.objects.get(pk=blogedit)
        blog.title = request.POST.get('title')
        blog.content = request.POST.get('content')
        blog.update_time = datetime.now()
        blog.status = status
        blog.save()
        # ----------------------------------------------

        return render(request, 'search/blog.html', context={'blog': blog})
    
    # ดึงข้อมูลบทความตามตัวแปรที่รับเข้ามา ( blogedit )
    blog = Post.objects.get(pk=blogedit)
    # ------------------------------------------

    return render(request, 'search/edit_blog.html', context={'blog': blog})

@login_required
@permission_required('blogger.add_post')
def post(request):
    if request.method == 'POST':

        # ----- รับ request เช็คดูว่าบทความถูกซ่อนหรือไม่ -----
        if request.POST.get('checkbox') == "Hide":
            status = False
        else:
            status = True
        # ----------------------------------------------

        # --------------- เพิ่มบทความใหม่ -----------------
        post = Post(
            user_id_id=1,
            title=request.POST.get('title'),
            content=request.POST.get('content'),
            create_time=datetime.now(),
            update_time = datetime.now(),
            status=status,
        )
        post.save()
        # ----------------------------------------------

        return render(request, 'search/blog.html', context={'blog': post})

    return render(request, 'search/post.html')

@login_required
@permission_required('blogger.change_comment')
def edit_com(request, comedit):
    if request.method == 'POST':
        
        # ------- แก้ไขความคิดเห็นตามตัวแปร comedit ---------
        com_new = Comment.objects.get(pk=comedit)
        com_new.content = request.POST.get('content')
        com_new.save()
        # ------------------------------------------------
        
        # ------------ ดึงข้อมูลบทความตาม id ของ Comment ----------------
        blog = Post.objects.get(pk=com_new.post_id.id)
        com = Comment.objects.filter(post_id_id=com_new.post_id.id)
        # -------------------------------------------------------------

        context = {
            'blog': blog,
            'com': com
        }
        return render(request, 'search/blog.html', context)

    # --- ดึงข้อมูล Comment ตามตัวแปร comedit ---
    com = Comment.objects.get(pk=comedit)
    # ---------------------------------------

    return render(request, 'search/edit_com.html', context={'com': com})

@login_required
@permission_required('blogger.delete_comment')
def com_remove(request, blog, com_remv):
    
    # ----------- ลบความคิดเห็น --------------
    com = Comment.objects.get(pk=com_remv)
    com.delete()
    # --------------------------------------

    # ----------- ดึงข้อมูลบทความตามตัวแปร blog ----------
    blog = Post.objects.get(pk=blog)
    all_com = Comment.objects.filter(post_id_id=blog)
    # -------------------------------------------------

    context = {
        'blog': blog,
        'com': all_com,
        'sign_page': "sign_page",
        'login_page': "login_page"
    }
    return render(request, 'search/blog.html', context)

@login_required
@permission_required('blogger.delete_post')
def post_remove(request, post_id):

    # ----------- ลบบทความ ---------------
    post = Post.objects.get(pk=post_id)
    post.delete()
    # -------------------------------------

    # ------------------- ดึงข้อมูล --------------------
    if request.user.is_superuser:
        post_all = Post.objects.all().order_by('id')
    else:
        post_all = Post.objects.filter(status=True).order_by('id')
    com = Post.objects.annotate(Count('comment'))
    com = com.values_list('id', 'comment__count')
    # -----------------------------------------------

    context = {
        'post_all': post_all,
        'com': com
    }
    return render(request, 'search/index.html', context)

@login_required
def change_pass(request):
    if request.method == 'POST':
        user = request.user
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # ---------------------- เช็คว่ารหัสผ่านตรงกันไหม ------------------
        if password1 == password2:
            u = User.objects.get(username=user)
            u.set_password(password1)
            u.save()
            return redirect('login')
        else:
            context = {
                'password1': password1,
                'password2': password2,
                'error': "กรุณากรอกรหัสผ่านให้ตรงกัน"
            }
            return render(request, 'search/changepass.html', context)
        # -------------------------------------------------------------

    return render(request, 'search/changepass.html')

@login_required
@permission_required('blogger.change_post')
def status(request, change_status):

    # --- ดึงข้อมูลและเช็ค status บทความว่าซ่อนอยู่หรือไม่ ---
    post = Post.objects.get(pk=change_status)
    if post.status:
        post.status = False
    else:
        post.status = True
    post.save()
    # -----------------------------------------------

    # ------------------- ดึงข้อมูล --------------------
    if request.user.is_superuser:
        post_all = Post.objects.all().order_by('id')
    else:
        post_all = Post.objects.filter(status=True).order_by('id')
        
    com = Post.objects.annotate(Count('comment'))
    com = com.values_list('id', 'comment__count')
    # -----------------------------------------------

    context = {
        'post_all': post_all,
        'com': com,
        'sign_page': "sign_page",
        'login_page': "login_page"
    }
    return render(request, 'search/index.html', context)
