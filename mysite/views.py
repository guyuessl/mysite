import datetime
from django.shortcuts import render_to_response
from read_statistics.utils import get_days_read_date, get_today_hot_data, get_hot_blogs
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from blog.models import Blog


def home(request):
	blog_content_type = ContentType.objects.get_for_model(Blog)
	read_nums, dates = get_days_read_date(blog_content_type)

	# 缓存7天热门博客数据
	week_hot_blogs = cache.get('week_hot_blogs')
	if week_hot_blogs is None:
		week_hot_blogs = get_hot_blogs(7)
		cache.set('week_hot_blogs', week_hot_blogs, 3600)
		
	context = {}
	context['read_nums'] = read_nums
	context['dates'] = dates
	context['today_hot_data'] = get_today_hot_data()
	context['yesterday_hot_data'] = get_hot_blogs(1)
	context['week_hot_blogs'] = week_hot_blogs
	return render_to_response('home.html', context)
