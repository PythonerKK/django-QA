from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth.mixins import LoginRequiredMixin
from django.template.loader import render_to_string
from django.views.generic import ListView, DeleteView

from utils.helpers import ajax_required, AuthorRequiredMixin
from zhihu.news.models import News


class NewsListView(LoginRequiredMixin, ListView):
    '''
    首页动态
    '''
    model = News
    #queryset = News.objects.all()
    paginate_by = 20
    #context_object_name = 'news_list'
    #ordering = 'created_at'
    #template_name = 'news/news_list.html'

    def get_queryset(self):
        return News.objects.filter(reply=False)


class NewsDeleteView(LoginRequiredMixin, AuthorRequiredMixin, DeleteView):
    model = News
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('news:list')


@login_required
@ajax_required
@require_POST
def post_new(request):
    '''
    发送动态 AJAX POST
    :param request:
    :return:
    '''
    post = request.POST['post'].strip()
    if post:
        posted = News.objects.create(
            user=request.user,
            content=post
        )
        html = render_to_string(
            'news/news_single.html',
            context={
                'news': posted,
                'request': request
            }
        )
        return HttpResponse(html)
    else:
        return HttpResponseBadRequest('内容不能为空')


@login_required
@ajax_required
@require_POST
def like(request):
    '''
    点赞
    :param request:
    :return:
    '''
    news_id = request.POST['news']
    news = News.objects.get(pk=news_id)
    news.switch_like(request.user)
    return JsonResponse({
        'likes': news.count_likers()
    })


@login_required
@ajax_required
@require_GET
def get_thread(request):
    '''
    返回动态评论 AJAX GET
    :param request:
    :return:
    '''
    news_id = request.GET['news']
    news = News.objects.get(pk=news_id)
    news_html = render_to_string('news/news_single.html', {'news': news}) #没有评论
    thread_html = render_to_string('news/news_thread.html', {'thread': news.get_thread()}) #有评论
    return JsonResponse({
        'uuid': news_id,
        'news': news_html,
        'thread': thread_html
    })



@login_required
@ajax_required
@require_POST
def post_comment(request):
    '''
    发表评论
    :param request:
    :return:
    '''
    post = request.POST['reply'].strip()
    parent_id = request.POST['parent']
    parent = News.objects.get(pk=parent_id)
    if post:
        parent.reply_this(request.user, post)
        return JsonResponse({
            'comments': parent.comment_count()
        })
    else:
        return HttpResponseBadRequest('请输入评论')
