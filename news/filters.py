from django.db.models import Q
from django_filters import rest_framework as filters
from news.models.news_model import News


class NewsFilter(filters.FilterSet):
    tags = filters.CharFilter(field_name='tags__name', lookup_expr='iexact')
    tags_list = filters.CharFilter(method='filter_tags_list')

    keyword = filters.CharFilter(field_name='text', lookup_expr='icontains')
    keywords = filters.CharFilter(method='filter_keywords')

    exclude_keyword = filters.CharFilter(method='filter_exclude_keyword')
    exclude_keywords = filters.CharFilter(method='filter_exclude_keywords')

    def filter_tags_list(self, queryset, name, value):
        tags = [tag.strip() for tag in value.split(',')]
        return queryset.filter(tags__name__in=tags).distinct()

    def filter_keywords(self, queryset, name, value):
        keywords = [keyword.strip() for keyword in value.split(',')]
        q_objects = Q()
        for keyword in keywords:
            q_objects |= Q(text__icontains=keyword) | Q(title__icontains=keyword)
        return queryset.filter(q_objects)

    def filter_exclude_keyword(self, queryset, name, value):
        return queryset.exclude(text__icontains=value)

    def filter_exclude_keywords(self, queryset, name, value):
        keywords = [keyword.strip() for keyword in value.split(',')]
        for keyword in keywords:
            queryset = queryset.exclude(text__icontains=keyword)
        return queryset

    class Meta:
        model = News
        fields = ['tags', 'tags_list', 'keyword', 'keywords', 'exclude_keyword', 'exclude_keywords']
