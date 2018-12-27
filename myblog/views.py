import datetime

from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone

from blog.models import Blog
from myblog.forms import LoginForm, RegForm
from read_statistics.utils import get_seven_days_data


# 获得一段时间内的热门博客
def get_hot_data(start_date, end_date):
    today = timezone.now().date()
    start_date = today - datetime.timedelta(days=start_date)
    end_date = today - datetime.timedelta(days=end_date)
    blogs = Blog.objects \
        .filter(read_details__date__lte=start_date, read_details__date__gte=end_date) \
        .values('id', 'title') \
        .annotate(read_num_sum=Sum('read_details__read_num')) \
        .order_by('-read_num_sum')
    return blogs[:7]


def home(request):
    blog_content_type = ContentType.objects.get_for_model(Blog)
    dates, read_nums = get_seven_days_data(blog_content_type)

    # 获取7天热门博客的缓存数据
    seven_days_hot_data = cache.get('seven_days_hot_data')
    if seven_days_hot_data is None:
        seven_days_hot_data = get_hot_data(1, 7)
        cache.set('seven_days_hot_data', seven_days_hot_data, 10)

    # 获取昨天热门博客的缓存数据
    yesterday_hot_data = cache.get('yesterday_hot_data')
    if yesterday_hot_data is None:
        yesterday_hot_data = get_hot_data(1, 1)
        cache.set('yesterday_hot_data', yesterday_hot_data, 3600)

    today_hot_data = get_hot_data(0, 0)

    context = {}
    context['today_hot_data'] = today_hot_data
    context['yesterday_hot_data'] = yesterday_hot_data
    context['seven_days_hot_data'] = seven_days_hot_data
    context['dates'] = dates
    context['read_nums'] = read_nums
    return render(request, 'home.html', context)


def login(request):
    if request.method == 'POST':
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            user = login_form.cleaned_data['user']
            auth.login(request, user)
            return redirect(request.GET.get('from', reverse('home')))
    else:
        login_form = LoginForm()

    context = {}
    context['login_form'] = login_form
    return render(request, 'login.html', context)


def login_for_medal(request):
    login_form = LoginForm(request.POST)
    data = {}
    if login_form.is_valid():
        user = login_form.cleaned_data['user']
        auth.login(request, user)
        data['status'] = 'SUCCESS'
    else:
        data['status'] = 'ERROR'
    return JsonResponse(data)


def register(request):
    if request.method == 'POST':
        reg_form = RegForm(request.POST)
        if reg_form.is_valid():
            username = reg_form.cleaned_data['username']
            email = reg_form.cleaned_data['email']
            password = reg_form.cleaned_data['password']
            # 创建用户
            user = User.objects.create_user(username, email, password)
            user.save()
            # 登录用户
            user = auth.authenticate(username=username, password=password)
            auth.login(request, user)
            return redirect(request.GET.get('from', reverse('home')))
    else:
        reg_form = RegForm()

    context = {}
    context['reg_form'] = reg_form
    return render(request, 'register.html', context)
