from django.shortcuts import render, redirect
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from .models import Comment


def update_comment(request):
	referer = request.META.get('HTTP_REFERER', reverse('home'))
	# 数据检查
	if not request.user.is_authenticated:
		return render(request, 'error.html', {'message': '用户不为空'}) 
	text = request.POST.get('text','')
	if text == '':
		return render(request, 'error.html', {'message': '评论内容为空'}) 
	try:
		content_type = request.POST.get('content_type', '')
		object_id = int(request.POST.get('object_id',''))
		model_class = ContentType.objects.get(model=content_type).model_class()
		content_object = model_class.objects.get(pk=object_id)
	except Exception as e:
		return render(request, 'error.html', {'message': '评论对象不存在', 'redirect_to': referer}) 

	# 检查通过，保存数据
	comment = Comment()
	comment.user = request.user
	comment.text = text
	comment.content_object = content_object
	comment.save()
	return redirect(referer)





