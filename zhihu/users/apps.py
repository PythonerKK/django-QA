from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UsersConfig(AppConfig):
    name = "zhihu.users"
    verbose_name = "用户"

    def ready(self):
        try:
            import zhihu.users.signals  # noqa F401
        except ImportError:
            pass
