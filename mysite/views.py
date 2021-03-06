import datetime
from django.shortcuts import render, redirect
from read_statistics.utils import get_days_read_date, get_today_hot_data, get_hot_blogs
from django.core.cache import cache
from django.contrib import auth
from django.urls import reverse
from django.contrib.auth.models import User
from .form import LoginForm, RegForm


def home(request):
	read_nums, dates = get_days_read_date()

	# 缓存7天热门博客数据
	week_hot_blogs = cache.get('week_hot_blogs')
	if week_hot_blogs is None:
		week_hot_blogs = get_hot_blogs(7)
		cache.set('week_hot_blogs', week_hot_blogs, 3600)#	缓存时间秒

	context = {}
	context['read_nums'] = read_nums
	context['dates'] = dates
	context['today_hot_data'] = get_today_hot_data()
	context['yesterday_hot_data'] = get_hot_blogs(1)
	context['week_hot_blogs'] = week_hot_blogs
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


def register(request):
	if request.method == 'POST':
		reg_form = RegForm(request.POST)
		if reg_form.is_valid():
			username = reg_form.cleaned_data['username']
			password = reg_form.cleaned_data['password']
			email = reg_form.cleaned_data['email']
			# 创建用户的方法
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
	    	