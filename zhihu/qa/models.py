import uuid
from collections import Counter

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey
from django.db import models
from django.utils.encoding import python_2_unicode_compatible


from markdownx.models import MarkdownxField
from markdownx.utils import markdownify
from slugify import slugify
from taggit.managers import TaggableManager

from zhihu.notifications.views import notification_handler
from zhihu.utils.models import CreatedUpdatedMixin


@python_2_unicode_compatible
class Vote(CreatedUpdatedMixin, models.Model):
    '''通用投票 关联问题和回答的投票'''
    uuid_id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                               editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='qa_vote',
                             on_delete=models.CASCADE)
    value = models.BooleanField(default=True, verbose_name='赞同或者反对')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE,
                                     related_name='vote_on')
    object_id = models.CharField(max_length=255)
    vote = GenericForeignKey()

    class Meta:
        verbose_name = '投票'
        verbose_name_plural = verbose_name
        unique_together = ('user', 'content_type', 'object_id')
        index_together = ('content_type', 'object_id')


@python_2_unicode_compatible
class QuestionQuerySet(models.query.QuerySet):
    '''
    自定义qs
    '''
    def get_answered(self):
        '''已有答案的问题'''
        return self.filter(has_answer=True).select_related('user')

    def get_unanswered(self):
        '''还没有答案的问题'''
        return self.filter(has_answer=False).select_related('user')

    def get_counted_tags(self):
        '''所有标签数量'''
        tag_dict = {}
        for obj in self.all():
            for tag in obj.tags.names():
                if tag not in tag_dict:
                    tag_dict[tag] = 1
                else:
                    tag_dict[tag] += 1

        return tag_dict.items()



@python_2_unicode_compatible
class Question(CreatedUpdatedMixin, models.Model):

    STATUS = (
        ('O', 'OPEN'),
        ('C', 'Close'),
        ('D', 'Draft')
    )

    title = models.CharField(max_length=255, unique=True, verbose_name='标题')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                             on_delete=models.CASCADE, related_name='q_author',
                             verbose_name='提问者')
    content = MarkdownxField(verbose_name='内容')
    slug = models.SlugField(max_length=255, null=True, blank=True, verbose_name='url别名')
    status = models.CharField(max_length=1, choices=STATUS, default='O',verbose_name='问题状态')
    tags = TaggableManager(help_text='多个标签，使用,隔开')
    has_answer = models.BooleanField(default=False, verbose_name='接受回答')
    votes = GenericRelation(Vote, verbose_name='投票情况')
    objects = QuestionQuerySet.as_manager()

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.slug:
            self.slug = slugify(self.title)
        super(Question, self).save(force_insert=False, force_update=False, using=None,
             update_fields=None)

    def __str__(self):
        return self.title

    def get_markdown(self):
        return markdownify(self.content)


    def total_votes(self):
        '''总票数'''
        d = Counter(self.votes.values_list('value', flat=True))
        return d[True] - d[False]


    def get_answers(self):
        '''获取所有的回答'''
        return Answer.objects.filter(question=self).select_related('user', 'question')

    def count_answers(self):
        '''回答数'''
        return self.get_answers().count()

    def get_upvoters(self):
        '''赞同的用户'''
        return [vote.user for vote in self.votes.filter(value=True).select_related('user').prefetch_related('votes')]

    def get_downvoters(self):
        '''踩的用户'''
        return [vote.user for vote in self.votes.filter(value=False).select_related('user').prefetch_related('votes')]

    def get_accepted_answers(self):
        '''获取被采纳的答案'''
        return Answer.objects.get(question=self, is_answer=True)

    class Meta:
        verbose_name = '问题'
        verbose_name_plural = verbose_name
        ordering = ('-created_at', )



@python_2_unicode_compatible
class Answer(CreatedUpdatedMixin, models.Model):
    uuid_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='a_author')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    content = MarkdownxField(verbose_name='内容')
    is_answer = models.BooleanField(default=False, verbose_name='是否被接受')

    votes = GenericRelation(Vote, verbose_name='投票情况')

    class Meta:
        verbose_name = '回答'
        verbose_name_plural = verbose_name
        ordering = ('-is_answer', '-created_at',)

    def __str__(self):
        return self.content

    def get_markdown(self):
        return markdownify(self.content)

    def total_votes(self):
        '''总票数'''
        d = Counter(self.votes.values_list('value', flat=True))
        return d[True] - d[False]

    def get_upvoters(self):
        '''赞同的用户'''
        return [vote.user for vote in self.votes.filter(value=True).select_related('user').prefetch_related('votes')]

    def get_downvoters(self):
        '''踩的用户'''
        return [vote.user for vote in self.votes.filter(value=False).select_related('user').prefetch_related('votes')]

    def accept_answer(self):
        '''接受回答'''

        answer_set = Answer.objects.filter(question=self.question).select_related('user', 'question')
        answer_set.update(is_answer=False) #把其他答案都设置为False

        self.is_answer = True #设置当前为采纳答案
        self.save()

        self.question.has_answer = True  #设置问题已经有采纳的答案
        self.question.save()


