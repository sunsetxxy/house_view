from django.urls import path
from rest_framework import routers

from house.views import (
    HouseViewSet, AreaListView, LocationListView, 
    HouseStatisticsView, HouseSinglePriceStatisticsView, 
    HousePriceStatisticsView, HouseAttributeStatisticsView,
    HouseCommunityStatisticsView, HouseUpdateView  # 添加HouseUpdateView导入
)

urlpatterns = [
    path('citylist',HouseViewSet.as_view(),name='citylist'),
    path('areas/', AreaListView.as_view(), name='area-list'),
    path('locations/', LocationListView.as_view(), name='location-list'),
    path('statistics/', HouseStatisticsView.as_view(), name='house-statistics'),
    path('price-statistics/', HousePriceStatisticsView.as_view(), name='house-price-statistics'),
    path('single-price-statistics/', HouseSinglePriceStatisticsView.as_view(), name='house-single-price-statistics'),
    path('attribute-statistics/', HouseAttributeStatisticsView.as_view(), name='house-attribute-statistics'),
    path('community-statistics/', HouseCommunityStatisticsView.as_view(), name='house-community-statistics'),
    
    # 添加房源信息修改接口
    path('house/update/', HouseUpdateView.as_view(), name='house_update'),
]
