from django_filters import rest_framework as filters
from house.models import city

class HouseFilter(filters.FilterSet):
    price_min = filters.NumberFilter(field_name='price', lookup_expr='gte')
    price_max = filters.NumberFilter(field_name='price', lookup_expr='lte')
    single_price_min = filters.NumberFilter(field_name='single_price', lookup_expr='gte')
    single_price_max = filters.NumberFilter(field_name='single_price', lookup_expr='lte')

    class Meta:
        model = city
        fields = ['city_name', 'localhost', 'type_name', 'floor', 'fitment']