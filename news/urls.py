from django.urls import path

from news.views import news_list_view, news_create_view, news_update_view, news_remove_view, scrap_news_view

app_name = 'news'

urlpatterns = [
    path('list/', news_list_view.NewsListView.as_view(), name='news-list'),
    path('create/', news_create_view.CreateNewsView.as_view(), name='news-create'),
    path('<str:news_id>/update/', news_update_view.UpdateNewsView.as_view(), name='news-update'),
    path('<str:news_id>/remove/', news_remove_view.RemoveNewsView.as_view(), name='news-remove'),
    path('scrape/', scrap_news_view.ScrapedNewsView.as_view(), name='news-scrape'),

]
