from django.conf import settings
from django.urls import include, path
from django.conf.urls.static import static

from django.views import defaults as default_views

urlpatterns = [

    path("users/", include("zhihu.users.urls", namespace="users")),
    path("accounts/", include("allauth.urls")),

    path('markdownx/', include('markdownx.urls')),
    path('comments/', include('django_comments.urls')),
    path('search/', include('haystack.urls')),

    path('news/', include('news.urls', namespace="news")),
    path('articles/', include('articles.urls', namespace='articles')),
    path('qa/', include('qa.urls', namespace='qa')),
    path('messages/', include('messager.urls', namespace='messages')),
    path('notifications/', include('notifications.urls', namespace='notifications')),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
