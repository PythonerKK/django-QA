from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, ListView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from django_comments.signals import comment_was_posted

from zhihu.articles.forms import ArticleForm
from zhihu.utils.helpers import AuthorRequiredMixin
from zhihu.articles.models import Article
from zhihu.notifications.views import notification_handler


class ArticlesListView(LoginRequiredMixin, ListView):
    '''文章列表'''
    model = Article
    paginate_by = 10
    context_object_name = 'articles'
    template_name = 'articles/article_list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        '''标签上下文'''
        context = super(ArticlesListView, self).get_context_data(
            object_list=None, **kwargs)
        context['popular_tags'] = Article.objects.get_counted_tags()
        return context

    def get_queryset(self):
        return Article.objects.get_publushed()


class DraftListView(ArticlesListView):
    '''草稿箱列表'''

    def get_queryset(self):
        return Article.objects.filter(user=self.request.user).get_drafts()


@method_decorator(cache_page(60 * 60), name='get')
class ArticleCreateView(LoginRequiredMixin, CreateView):
    '''发表文章'''
    model = Article
    form_class = ArticleForm
    template_name = 'articles/article_create.html'
    message = '文章已经创建成功'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(ArticleCreateView, self).form_valid(form)

    def get_success_url(self):
        '''成功后跳转'''
        messages.success(self.request, self.message)
        return reverse_lazy('articles:list')



class ArticleDetailView(LoginRequiredMixin, DetailView):
    '''详情'''
    model = Article
    template_name = 'articles/article_detail.html'

    def get_queryset(self):
        return Article.objects.select_related('user').filter(
            slug=self.kwargs['slug'])


class ArticleEditView(LoginRequiredMixin, AuthorRequiredMixin, UpdateView):
    '''用户编辑文章'''
    model = Article
    message = '文章编辑成功'
    template_name = 'articles/article_update.html'
    form_class = ArticleForm

    def form_valid(self, form):
        form.instance = self.request.user
        return super(ArticleEditView, self).form_valid(form)

    def get_success_url(self):
        messages.success(self.request, self.message)
        return reverse('articles:article', kwargs={'slug': self.get_object().slug})


def notify_comment(**kwargs):
    '''文章有评论通知作者'''
    actor = kwargs['request'].user
    obj = kwargs['comment'].content_object
    print(obj)
    notification_handler(
        actor,
        obj.user,
        'C',
        obj
    )
comment_was_posted.connect(receiver=notify_comment)
