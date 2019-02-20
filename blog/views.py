from django.shortcuts import render_to_response, get_object_or_404
from django.core.paginator import Paginator
from django.conf import settings
from .models import Blog, BlogType
from django.db.models import Count
from read_statistics.utils import read_statistics_once_read


#   博客列表页数据处理
def blog_list(request):
    blogs_all_list = Blog.objects.all()
    context = get_blog_list_common_data(request, blogs_all_list)
    return render_to_response('blog/blog_list.html', context)


#   博客内容页数据处理
def blog_detail(request, blog_pk):
    blog = get_object_or_404(Blog, pk=blog_pk)
    read_cookie_key = read_statistics_once_read(request, blog)
    context = {}
    context['previous_blog'] = Blog.objects.filter(created_time__gt=blog.created_time).last()
    context['next_blog'] = Blog.objects.filter(created_time__lt=blog.created_time).first()
    context['blog'] = blog
    response = render_to_response('blog/blog_detail.html', context)
    response.set_cookie(read_cookie_key, 'true', max_age=15) # 阅读cookie标记 第三个参数是控制过期时间，不加就是关闭浏览器就算是过期
    return response


#   博客分类列表页数据处理
def blogs_with_type(request, blog_type_pk):
    blog_type = get_object_or_404(BlogType, pk=blog_type_pk)
    blogs_all_list = Blog.objects.filter(blog_type = blog_type)
    context = get_blog_list_common_data(request, blogs_all_list)
    context['blogtype'] = blog_type
    return render_to_response('blog/blogs_with_type.html', context)


def blogs_with_date(request, year, month):
    blogs_all_list = Blog.objects.filter(created_time__year=year, created_time__month=month)
    context = get_blog_list_common_data(request, blogs_all_list)
    context['blog_with_date'] = "%s年%s月" % (year,month)
    return render_to_response('blog/blogs_with_date.html', context)

#   合并重复使用的数据
def get_blog_list_common_data(request, blogs_all_list):
    paginator = Paginator(blogs_all_list, settings.EACH_PAGE_BLOG_NUMBER)   #   每几个分一页
    page_num = request.GET.get('page', 1)    #   获取页码参数 GET请求
    page_of_blogs = paginator.get_page(page_num)    #   获取该页的数据   
    current_page_num = page_of_blogs.number    #    获取当前页

    page_range = list(range(max(current_page_num-2,1),current_page_num))+\
                list(range(current_page_num, min(current_page_num+2, paginator.num_pages)+1))   #   获取当前的页码列表

    #   加省略号
    if page_range[0] -1 >= 2:
        page_range.insert(0, '...')
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')    

    #   加首尾页
    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)

    # 获取日期归档对应的博客数量
    blog_dates = Blog.objects.dates('created_time', 'month', order='DESC')
    blog_date_dict = {}
    for blog_date in blog_dates:
        blog_count = Blog.objects.filter(created_time__year=blog_date.year, 
                            created_time__month=blog_date.month).count()
        blog_date_dict[blog_date] = blog_count


    context = {}
    context['blogs'] = page_of_blogs.object_list
    context['page_of_blogs'] = page_of_blogs
    context['page_range'] = page_range
    context['blogs_types'] = BlogType.objects.annotate(blog_count=Count('blog'))
    context['blog_dates'] = blog_date_dict
    return context