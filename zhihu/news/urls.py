from django.urls import path

from zhihu.news import views

app_name = "news"
urlpatterns = [
    path("", view=views.NewsListView.as_view(), name="list"),
    path('post-news/', view=views.post_new, name='post_news'),
    path('like/', view=views.like, name='like_post'),
    path('get-thread/', view=views.get_thread, name='get_thread'),
    path('post-comment/', view=views.post_comment, name='post_comment'),
    path('delete/<str:pk>', view=views.NewsDeleteView.as_view(), name='delete_news'),
]
