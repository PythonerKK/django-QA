from django.conf import settings
from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from markdownx.models import MarkdownxField
from markdownx.utils import markdownify
from taggit.managers import TaggableManager
from slugify import slugify

from zhihu.utils.models import CreatedUpdatedMixin


@python_2_unicode_compatible
class ArticleQuerySet(models.query.QuerySet):
    '''
    自定义qs
    '''
    def get_publushed(self):
        '''获取已发表的'''
        return self.filter(status='P').select_related('user')

    def get_drafts(self):
        ''''''
        return self.filter(status='D').select_related('user')

    def get_counted_tags(self):
        '''所有标签数量'''
        tag_dict = {}
        query = self.get_publushed().annotate(
            tagged=models.Count('tags')).filter(tags__gt=0)
        for obj in query:
            for tag in obj.tags.names():
                if tag not in tag_dict:
                    tag_dict[tag] = 1
                else:
                    tag_dict[tag] += 1

        return tag_dict.items()


@python_2_unicode_compatible
class Article(CreatedUpdatedMixin, models.Model):

    STATUS = (
        ('D', 'Draft'),
        ('P', 'published')
    )

    title = models.CharField(max_length=255, unique=True, verbose_name='标题')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                             on_delete=models.SET_NULL, related_name='author',
                             verbose_name='作者')
    image = models.ImageField(upload_to='articles_pictures/%Y/%m/%d/', verbose_name='图片')
    slug = models.SlugField(max_length=255, verbose_name='url别名')
    status = models.CharField(max_length=1, choices=STATUS, default='D',verbose_name='状态')
    content = MarkdownxField(verbose_name='内容')
    edited = models.BooleanField(default=False, verbose_name='是否可编辑')
    tags = TaggableManager(help_text='多个标签，使用,隔开')

    objects = ArticleQuerySet.as_manager()

    class Meta:
        verbose_name = '文章'
        verbose_name_plural = verbose_name
        ordering = ('-created_at', )

    def __str__(self):
        return self.title

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.slug = slugify(self.title)

        super(Article, self).save(force_insert=False, force_update=False, using=None,
             update_fields=None)

    def get_markdown(self):
        '''markdown->html'''
        return markdownify(self.content)
