from rest_framework import fields, serializers
from rest_framework.serializers import BaseSerializer, Serializer, ModelSerializer
from house.models import city



# 修改序列化器，添加新字段
class HouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = city
        fields = ['id', 'house_name', 'city_name', 'localhost', 'price', 'type_name', 
                 'use_area', 'single_price', 'forword', 'floor', 'fitment', 'url', 
                 'city', 'city_id', 'area_id', 'location_id']  # 添加三个 ID 字段


class PageSerializer(ModelSerializer):
    class Meta:
        model = city
        fields = ['page', 'page_size'
        
]
