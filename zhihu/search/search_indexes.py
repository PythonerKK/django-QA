from datetime import datetime

from haystack import indexes
from zhihu.news.models import News
from zhihu.articles.models import Article
from zhihu.qa.models import Question
from django.contrib.auth import get_user_model
from taggit.models import Tag


class ArticleIndex(indexes.SearchIndex, indexes.Indexable):
    '''文章模型建立索引'''
    text = indexes.CharField(document=True, use_template=True,
                             template_name='search/articles_text.txt')

    def get_model(self):
        # 这里修改成你自己的数据库模型
        return Article

    def index_queryset(self, using=None):
        '''索引更新时调用'''
        return self.get_model().objects.filter(status="P",
                                               updated_at__lte=datetime.now())


class NewsIndex(indexes.SearchIndex, indexes.Indexable):
    '''文章模型建立索引'''
    text = indexes.CharField(document=True, use_template=True,
                             template_name='search/news_text.txt')

    def get_model(self):
        # 这里修改成你自己的数据库模型
        return News

    def index_queryset(self, using=None):
        '''索引更新时调用'''
        return self.get_model().objects.filter(reply=False,
                                               updated_at__lte=datetime.now())


class QuestionIndex(indexes.SearchIndex, indexes.Indexable):
    '''文章模型建立索引'''
    text = indexes.CharField(document=True, use_template=True,
                             template_name='search/questions_text.txt')

    def get_model(self):
        # 这里修改成你自己的数据库模型
        return Question

    def index_queryset(self, using=None):
        '''索引更新时调用'''
        return self.get_model().objects.filter(updated_at__lte=datetime.now())


class TagsIndex(indexes.SearchIndex, indexes.Indexable):
    '''文章模型建立索引'''
    text = indexes.CharField(document=True, use_template=True,
                             template_name='search/tags_text.txt')

    def get_model(self):
        # 这里修改成你自己的数据库模型
        return Tag

    def index_queryset(self, using=None):
        '''索引更新时调用'''
        return self.get_model().objects.all()

