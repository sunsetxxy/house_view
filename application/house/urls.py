from django.urls import path
from rest_framework import routers

from house.views import HouseViewSet,AreaListView,LocationListView
from house.models import city

urlpatterns= [
    path('citylist',HouseViewSet.as_view(),name='citylist'),
    path('areas/', AreaListView.as_view(), name='area-list'),
    path('locations/', LocationListView.as_view(), name='location-list'),
]
