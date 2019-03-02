from django import template
from django.contrib.contenttypes.models import ContentType
from django.db.models.fields import exceptions
from ..models import Comment
from ..forms import CommentForm
from read_statistics.models import ReadNum


register = template.Library()


@register.simple_tag
def get_comment_count(obj):
	obj_content_type = ContentType.objects.get_for_model(obj)
	return Comment.objects.filter(content_type = obj_content_type, object_id=obj.pk).count()


@register.simple_tag
def get_comment_form(obj):
	obj_content_type = ContentType.objects.get_for_model(obj)
	form = CommentForm(initial={'content_type':  obj_content_type.model, 'object_id': obj.pk, 'reply_comment_id': 0})
	return form


@register.simple_tag
def get_comment_list(obj):
	obj_content_type = ContentType.objects.get_for_model(obj)
	comments = Comment.objects.filter(content_type = obj_content_type, object_id=obj.pk, parent=None)
	return comments.order_by('-comment_time')


@register.simple_tag
def get_blog_read_num(obj):
	try:
		obj_content_type = ContentType.objects.get_for_model(obj)
		readnum = ReadNum.objects.get(content_type=obj_content_type, object_id=obj.pk)
		return readnum.read_num
	except exceptions.ObjectDoesNotExist:
		return 0