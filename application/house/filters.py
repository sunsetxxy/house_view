import django_filters
from django_filters import rest_framework as filters
from house.models import city

class HouseFilter(django_filters.FilterSet):
    price_min = filters.NumberFilter(field_name='price', lookup_expr='gte')
    price_max = filters.NumberFilter(field_name='price', lookup_expr='lte')
    single_price_min = filters.NumberFilter(field_name='single_price', lookup_expr='gte')
    single_price_max = filters.NumberFilter(field_name='single_price', lookup_expr='lte')
    city_id = django_filters.NumberFilter(field_name='city_id')
    area_id = django_filters.NumberFilter(field_name='area_id')
    location_id = django_filters.NumberFilter(field_name='location_id')

    class Meta:
        model = city
        fields = ['city_name', 'localhost', 'type_name', 'floor', 'fitment', 
                 'city_id', 'area_id', 'location_id']