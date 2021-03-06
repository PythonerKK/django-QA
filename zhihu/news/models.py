import uuid

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from zhihu.notifications.views import notification_handler
from zhihu.utils.models import CreatedUpdatedMixin


@python_2_unicode_compatible
class News(CreatedUpdatedMixin, models.Model):
    uuid_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True,
                             on_delete=models.SET_NULL, related_name='publisher',
                             verbose_name='用户')
    parent = models.ForeignKey('self', blank=True, null=True, on_delete=models.CASCADE,
                               related_name='thread', verbose_name='自关联')

    content = models.TextField(verbose_name='动态内容')
    liked = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                   related_name='liked_news', verbose_name='点赞用户')
    reply = models.BooleanField(default=False, verbose_name='是否为评论')


    class Meta:
        verbose_name = '首页'
        verbose_name_plural = verbose_name
        ordering = ('-created_at',)

    def __str__(self):
        return self.content

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):

        super(News, self).save(force_insert=False, force_update=False, using=None,
             update_fields=None)
        if not self.reply:
            channel_layer = get_channel_layer()
            payload = {
                'type': 'receive',
                'key': 'additional_news',
                'actor_name': self.user.username,
            }
            async_to_sync(channel_layer.group_send)('notifications', payload)


    def switch_like(self, user):
        '''点赞或取消赞'''
        #已经赞了，取消
        #如果没有赞，添加
        if user in self.liked.all():
            self.liked.remove(user)
        else:
            self.liked.add(user)

            # 通知楼主
            notification_handler(
                actor=user,
                recipient=self.user,
                verb='L',
                action_object=self,
                key='social_update',
                id_value=str(self.pk)
            )


    def get_parent(self):
        """返回上级记录或者自己"""
        if self.parent:
            return self.parent
        else:
            return self


    def reply_this(self, user, text):
        '''
        回复首页的动态
        :param user: 登录的用户
        :param text: 回复的内容
        :return:
        '''
        parent = self.get_parent()
        News.objects.create(
            user=user,
            content=text,
            reply=True,
            parent=parent
        )
        notification_handler(
            actor=user,
            recipient=parent.user,
            verb='R',
            action_object=parent,
            key='social_update',
            id_value=str(parent.pk)
        )

    def get_thread(self):
        '''
        获取关联到当前记录的所有记录
        :return:
        '''
        parent = self.get_parent()
        return parent.thread.all()

    def comment_count(self):
        '''
        评论数
        :return:
        '''
        return self.get_thread().count()


    def count_likers(self):
        '''
        点赞数
        :return:
        '''
        return self.liked.count()

    def get_likers(self):
        '''
        获取点赞的用户
        :return:
        '''
        return self.liked.all()
