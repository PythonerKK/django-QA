from django.apps import AppConfig


class ArticlesConfig(AppConfig):
    name = 'zhihu.articles'
    verbose_name = '文章'

    def ready(self):
        try:
            import zhihu.articles.signals
        except ImportError:
            pass
