from django.apps import AppConfig


class NewsConfig(AppConfig):
    name = 'zhihu.news'
    verbose_name = '知乎'

    def ready(self):
        try:
            import zhihu.news.signals
        except ImportError:
            pass
