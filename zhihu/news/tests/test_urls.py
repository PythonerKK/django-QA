from test_plus import TestCase
from django.urls import resolve, reverse


class TestNewsUrls(TestCase):

    def setUp(self) -> None:
        self.user = self.make_user()

    def test_news_list_reverse(self):
        self.assertEqual(
            reverse('news:list'),
            '/news/'
        )

    def test_news_list_resolve(self):
        self.assertEqual(
            resolve('/news/').view_name,
            'news:list'
        )

