from django.urls import path
from rest_framework import routers

from house.views import HouseViewSet, AreaListView, LocationListView, HouseStatisticsView, HousePriceStatisticsView, HouseSinglePriceStatisticsView, HouseAttributeStatisticsView
from house.models import city

urlpatterns= [
    path('citylist',HouseViewSet.as_view(),name='citylist'),
    path('areas/', AreaListView.as_view(), name='area-list'),
    path('locations/', LocationListView.as_view(), name='location-list'),
    path('statistics/', HouseStatisticsView.as_view(), name='house-statistics'),
    path('price-statistics/', HousePriceStatisticsView.as_view(), name='house-price-statistics'),
    path('single-price-statistics/', HouseSinglePriceStatisticsView.as_view(), name='house-single-price-statistics'),
    path('attribute-statistics/', HouseAttributeStatisticsView.as_view(), name='house-attribute-statistics'),
]
