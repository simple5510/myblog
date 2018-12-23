import datetime

from django.core.cache import cache
from django.db.models import Sum
from django.shortcuts import render_to_response
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from read_statistics.utils import get_seven_days_data
from blog.models import Blog


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
    return render_to_response('home.html', context)
