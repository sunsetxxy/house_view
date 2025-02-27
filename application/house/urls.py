from django.urls import path
from rest_framework import routers

from house.views import HouseViewSet
from house.models import city

urlpatterns= [
    path('citylist',HouseViewSet.as_view(),name='citylist'),
]