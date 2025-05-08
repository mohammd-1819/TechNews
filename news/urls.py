from django.urls import path
from news.views import news_list_view

app_name = 'news'

urlpatterns = [
    path('list/', news_list_view.NewsListView.as_view(), name='news-list')
]
