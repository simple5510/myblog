import datetime

from django.contrib.contenttypes.models import ContentType
from django.db.models import Sum
from django.utils import timezone

from .models import ReadNum,ReadDetails


def read_statistics_once_read(request, obj):
    ct = ContentType.objects.get_for_model(obj)
    key = '%s_%s_read'%(ct.model,obj.pk)
    if not request.COOKIES.get(key):
       # 总阅读数加一
        read_num, created = ReadNum.objects.get_or_create(content_type=ct, object_id=obj.pk)
        read_num.read_num += 1
        read_num.save()
        # 当天阅读数加一
        date = timezone.now().date()
        read_detail, created = ReadDetails.objects.get_or_create(content_type=ct, object_id=obj.pk, date=date)
        read_detail.read_num += 1
        read_detail.save()
    return key


def get_seven_days_data(content_type):
    today = timezone.now().date()
    dates = []
    read_nums = []
    for i in range(7,0,-1):
        date = today - datetime.timedelta(days = i )
        dates.append(date.strftime('%m/%d'))
        read_details = ReadDetails.objects.filter(content_type=content_type, date=date)
        result = read_details.aggregate(read_num_sum = Sum('read_num'))
        read_nums.append(result['read_num_sum'] or 0)
    return dates, read_nums