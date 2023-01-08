from rest_framework import filters
from django_filters import rest_framework as filters
from reviews.models import Title


class CustomFilter(filters.BaseInFilter, filters.CharFilter):
    pass


class GenreFilter(filters.FilterSet):
    genre = CustomFilter(field_name='genre__slug', lookup_expr='in')
    category = CustomFilter(field_name='category__slug',)
    name = CustomFilter(field_name='name',)
    year = CustomFilter(field_name='year',)

    class Meta:
        model = Title
        fields = ['genre', 'category', 'name', 'year',]
