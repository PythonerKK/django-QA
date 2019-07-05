from test_plus import TestCase
from zhihu.news.models import News


class NewsModelTest(TestCase):

    def setUp(self) -> None:
        self.user = self.make_user('user01')
        self.other_user = self.make_user('user02')
        self.first_news = News.objects.create(
            user=self.user,
            content='first'
        )
        self.second_news = News.objects.create(
            user=self.user,
            content='second'
        )
        self.third_news = News.objects.create(
            user=self.other_user,
            content='comment first',
            reply=True,
            parent=self.first_news
        )

    def test__str__(self):
        self.assertEqual(self.first_news.__str__(), 'first')

    def test_switch_liked(self):
        '''测试点赞和取消'''
        self.first_news.switch_like(self.user)
        assert self.first_news.count_likers() == 1
        assert self.user in self.first_news.get_likers()

    def test_reply_this(self):
        '''测试回复'''
        self.first_news.reply_this(
            self.other_user,
            '评论第一条动态'
        )
        assert self.first_news.comment_count() == 2
        assert self.third_news in self.first_news.get_thread()
