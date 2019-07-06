from test_plus import TestCase
from zhihu.articles.models import Article


class ArticleModelsTest(TestCase):

    def setUp(self) -> None:
        self.user = self.make_user()
        self.draft = Article.objects.create(
            user=self.user,
            title='第一篇文章',
            content='测试',
            image='articles_pictures/2019/07/06/1.png',
            status='D',
            tags=['a', 'b']
        )
        self.published = Article.objects.create(
            user=self.user,
            title='第二篇文章',
            content='测试',
            image='articles_pictures/2019/07/06/1.png',
            status='P',
            tags=['a', 'b']
        )

    def test_object_instance(self):
        '''判断实例是否为article模型类'''
        assert isinstance(self.draft, Article)
        assert isinstance(self.published, Article)
        assert Article.objects.get_publushed().count() == 1
        assert Article.objects.get_publushed().first() == self.published
        assert Article.objects.get_drafts().count() == 1
        assert Article.objects.get_drafts().first() == self.draft
        assert self.draft.slug == 'di-yi-pian-wen-zhang'


    # def test_return_value(self):
    #     '''测试返回值'''
    #
    #
