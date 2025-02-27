from rest_framework import fields, serializers
from rest_framework.serializers import BaseSerializer, Serializer, ModelSerializer
from house.models import city



class HouseSerializer(ModelSerializer):
    class Meta:
        model = city
        fields = ['id', 'house_name','city_name','localhost','price','type_name','use_area','single_price','forword','floor','fitment','url']


class PageSerializer(ModelSerializer):
    class Meta:
        model = city
        fields = ['page', 'page_size'
        
]
