import datetime
from django.contrib.contenttypes.models import ContentType
from .models import ReadNum, ReadDetail
from django.utils import timezone
from django.db.models import Sum
from blog.models import Blog



#	累加博客阅读数，返回cookies的键
def read_statistics_once_read(request,obj):
	ct = ContentType.objects.get_for_model(obj)
	key = "%s_%s_read" % (ct.model, obj.pk)
	if not request.COOKIES.get(key):
		# 总阅读数 + 1
		readnum, created = ReadNum.objects.get_or_create(content_type=ct, object_id=obj.pk)
		readnum.read_num += 1
		readnum.save()

		# 当天阅读数+1
		date = timezone.now().date()
		readdetail, created = ReadDetail.objects.get_or_create(content_type=ct, object_id=obj.pk, date=date)
		readdetail.read_num += 1
		readdetail.save()
	return key


#	获取7内所有博客每天的阅读数
def get_days_read_date():
	today = timezone.now().date()
	read_nums = []
	dates = []
	for i in range(7, 0, -1):
		date = today - datetime.timedelta(days=i)
		dates.append(date.strftime('%m/%d'))
		result = Blog.objects \
						.filter(read_details__date=date) \
						.aggregate(read_num_sum=Sum('read_details__read_num'))

		read_nums.append(result['read_num_sum'] or 0)
	return read_nums, dates


#  获取今天点击的博客
def get_today_hot_data():
	today = timezone.now().date()
	blogs = Blog.objects \
					.filter(read_details__date=today) \
					.values('id', 'title') \
					.annotate(read_num_sum=Sum('read_details__read_num')) \
					.order_by('-read_num_sum')

	return blogs[:7]

#	获取点击的博客
def get_hot_blogs(day):
	today = timezone.now().date()
	date = today - datetime.timedelta(days=day)
	blogs = Blog.objects \
					.filter(read_details__date__lt=today, read_details__date__gte=date) \
					.values('id', 'title') \
					.annotate(read_num_sum=Sum('read_details__read_num')) \
					.order_by('-read_num_sum')

	return blogs[:7]