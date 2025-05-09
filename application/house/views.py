from django.shortcuts import render

# Create your views here.
from rest_framework.viewsets import ModelViewSet
from house.models import city
from django.http import JsonResponse
from django.views import View
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import SessionAuthentication
import json
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import GenericAPIView
from house.serializer import HouseSerializer
from rest_framework.response import Response
from rest_framework import filters 
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from house.filters import HouseFilter
from house.models import city, Area, Location
from django.db.models import Count, Sum, Avg, F, ExpressionWrapper, DecimalField
from django.db.models.functions import Coalesce

# 导入聚类分析所需的库
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, OneHotEncoder # 添加 OneHotEncoder
from sklearn.compose import ColumnTransformer # 添加 ColumnTransformer
from sklearn.decomposition import PCA
import pandas as pd


class HousePagination(PageNumberPagination):
    page_size = 30  # 每页显示的条目数
    page_size_query_param = 'size'  # 修改为size参数
    max_page_size = 100

class HouseViewSet(GenericAPIView):
    authentication_classes = (
        SessionAuthentication,
        JWTAuthentication
    )
    pagination_class = HousePagination
    serializer_class = HouseSerializer
                            #精准查询，                  模糊查询              范围查询
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]  # 添加搜索过滤器
    filterset_fields = ['city_name', 'localhost', 'type_name', 'floor', 'fitment']
    queryset = city.objects.all()
    filterset_class = HouseFilter 
    ordering_fields = ['price', 'single_price']  # 添加排序字段
    search_fields = ['house_name']  # 添加模糊搜索字段
    
    @swagger_auto_schema(
        operation_summary='获取房屋列表',
        operation_description='获取房屋信息，支持多种筛选条件',
        manual_parameters=[
            openapi.Parameter('city_name', openapi.IN_QUERY, description='区域名称', type=openapi.TYPE_STRING),
            openapi.Parameter('localhost', openapi.IN_QUERY, description='具体位置', type=openapi.TYPE_STRING),
            openapi.Parameter('type_name', openapi.IN_QUERY, description='户型', type=openapi.TYPE_STRING),
            openapi.Parameter('floor', openapi.IN_QUERY, description='楼层', type=openapi.TYPE_STRING),
            openapi.Parameter('fitment', openapi.IN_QUERY, description='装修', type=openapi.TYPE_STRING),
            openapi.Parameter('price_min', openapi.IN_QUERY, description='最低价格', type=openapi.TYPE_NUMBER),
            openapi.Parameter('price_max', openapi.IN_QUERY, description='最高价格', type=openapi.TYPE_NUMBER),
            openapi.Parameter('single_price_min', openapi.IN_QUERY, description='最低单价', type=openapi.TYPE_NUMBER),
            openapi.Parameter('single_price_max', openapi.IN_QUERY, description='最高单价', type=openapi.TYPE_NUMBER),
            openapi.Parameter('ordering', openapi.IN_QUERY, description='排序方式(price/-price/single_price/-single_price)', type=openapi.TYPE_STRING),
            openapi.Parameter('search', openapi.IN_QUERY, description='房屋名称模糊搜索', type=openapi.TYPE_STRING),
            openapi.Parameter('city_id', openapi.IN_QUERY, description='城市ID', type=openapi.TYPE_INTEGER),
            openapi.Parameter('area_id', openapi.IN_QUERY, description='区域ID', type=openapi.TYPE_INTEGER),
            openapi.Parameter('location_id', openapi.IN_QUERY, description='位置ID', type=openapi.TYPE_INTEGER),
        ]
    )
    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return Response({
                'code': '200',
                'info': '获取成功',
                'data': serializer.data,
                'count': queryset.count(),
                'current_page': request.query_params.get('page', 1),
                'page_size': request.query_params.get('size', 30),
                'next': self.paginator.get_next_link(),
                'previous': self.paginator.get_previous_link()
            }, status=status.HTTP_200_OK)
        
        return Response({
            'code': '200',
            'info': '获取成功',
            'data': [],
            'count': 0
        }, status=status.HTTP_200_OK)

class AreaListView(APIView):
    authentication_classes = (
        SessionAuthentication,
        JWTAuthentication
    )
    permission_classes = [IsAuthenticated]  # 添加权限控制

    @swagger_auto_schema(
        operation_summary='获取区域列表',
        operation_description='根据城市ID获取对应的区域列表',
        manual_parameters=[
            openapi.Parameter('city_id', openapi.IN_QUERY, description='城市ID', type=openapi.TYPE_INTEGER, required=True),
        ],
        responses={
            200: openapi.Response('成功获取区域列表', examples={
                'application/json': {
                    'code': '200',
                    'info': '获取成功',
                    'data': [
                        {
                            'id': 1,
                            'name': '区域名称'
                        }
                    ],
                    'total': 1
                }
            }),
            400: openapi.Response('参数错误'),
            401: openapi.Response('未认证'),
        }
    )
    def get(self, request):
        try:
            city_id = request.query_params.get('city_id')
            if not city_id or not city_id.isdigit():
                return Response({
                    'code': '400',
                    'info': '缺少城市ID参数',
                    'data': []
                }, status=status.HTTP_400_BAD_REQUEST)

            areas = Area.objects.filter(city_id=city_id).values('id', 'name')
            
            return Response({
                'code': '200',
                'info': '获取成功',
                'data': list(areas)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'code': '500',
                'info': '服务器内部错误',
                'data': []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LocationListView(APIView):
    authentication_classes = (
        SessionAuthentication,
        JWTAuthentication
    )
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary='获取位置列表',
        operation_description='根据区域ID获取对应的位置列表',
        manual_parameters=[
            openapi.Parameter('area_id', openapi.IN_QUERY, description='区域ID', type=openapi.TYPE_INTEGER, required=True),
        ],
        responses={
            200: openapi.Response('成功获取位置列表', examples={
                'application/json': {
                    'code': '200',
                    'info': '获取成功',
                    'data': [
                        {
                            'id': 1,
                            'location': '具体位置'
                        }
                    ],
                    'total': 1
                }
            }),
            400: openapi.Response('参数错误'),
            401: openapi.Response('未认证'),
        }
    )
    def get(self, request):
        try:
            area_id = request.query_params.get('area_id')
            if not area_id or not area_id.isdigit():
                return Response({
                    'code': '400',
                    'info': '无效的区域ID参数',
                    'data': []
                }, status=status.HTTP_400_BAD_REQUEST)

            locations = Location.objects.filter(area_id=area_id).values('id', 'location').order_by('id')
            
            return Response({
                'code': '200',
                'info': '获取成功',
                'data': list(locations),
                'total': locations.count()
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'code': '500',
                'info': '服务器内部错误',
                'data': []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HouseStatisticsView(APIView):
    authentication_classes = (
        SessionAuthentication,
        JWTAuthentication
    )
    
    @swagger_auto_schema(
        operation_summary='获取房源数量统计',
        operation_description='获取各区域房源数量统计，按数量从大到小排序',
        manual_parameters=[
            openapi.Parameter('city_id', openapi.IN_QUERY, description='城市ID(可选)', type=openapi.TYPE_INTEGER, required=False),
            openapi.Parameter('group_by', openapi.IN_QUERY, description='分组方式(city/area/location)，默认为area', type=openapi.TYPE_STRING, required=False),
            openapi.Parameter('limit', openapi.IN_QUERY, description='返回数据条数限制，默认为10', type=openapi.TYPE_INTEGER, required=False),
        ],
        responses={
            200: openapi.Response('成功获取统计数据'),
            400: openapi.Response('参数错误'),
            500: openapi.Response('服务器内部错误'),
        }
    )
    def get(self, request):
        try:
            city_id = request.query_params.get('city_id')
            group_by = request.query_params.get('group_by', 'area')  # 默认按区域分组
            limit = request.query_params.get('limit', 10)
            
            try:
                limit = int(limit)
            except (ValueError, TypeError):
                limit = 10
                
            # 初始化查询集
            queryset = city.objects.all()
            
            # 如果提供了城市ID，则过滤特定城市的数据
            if city_id and city_id.isdigit():
                queryset = queryset.filter(city_id=city_id)
            
            # 根据分组方式进行统计
            if group_by == 'city':
                # 按城市分组统计
                statistics = queryset.values('city_id', 'city_name')\
                    .annotate(count=Count('id'))\
                    .order_by('-count')[:limit]
                
                result = [
                    {
                        'name': item['city_name'],
                        'value': item['count'],
                        'id': item['city_id']
                    } for item in statistics
                ]
                
            elif group_by == 'location':
                # 按具体位置分组统计
                statistics = queryset.values('localhost')\
                    .annotate(count=Coalesce(Count('id'), 0))\
                    .filter(count__gt=0)\
                    .order_by('-count')[:limit]
                
                result = [
                    {
                        'name': item['localhost'] or '未知位置',
                        'value': item['count']
                    } for item in statistics
                ]
                
            else:  # 默认按区域分组
                # 按区域分组统计
                statistics = queryset.values('area_id')\
                    .annotate(count=Count('id'))\
                    .filter(count__gt=0)\
                    .order_by('-count')[:limit]
                
                # 获取区域名称
                result = []
                for item in statistics:
                    area_obj = Area.objects.filter(id=item['area_id']).first()
                    area_name = area_obj.name if area_obj else '未知区域'
                    result.append({
                        'name': area_name,
                        'value': item['count']
                    })
            
            return Response({
                'code': '200',
                'info': '获取成功',
                'data': result
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'code': '500',
                'info': f'服务器内部错误: {str(e)}',
                'data': []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HouseSinglePriceStatisticsView(APIView):
    authentication_classes = (
        SessionAuthentication,
        JWTAuthentication
    )
    
    @swagger_auto_schema(
        operation_summary='获取地区房源单价统计',
        operation_description='获取各地区房源平均单价统计，按单价从大到小排序',
        manual_parameters=[
            openapi.Parameter('city_id', openapi.IN_QUERY, description='城市ID(可选)', type=openapi.TYPE_INTEGER, required=False),
            openapi.Parameter('group_by', openapi.IN_QUERY, description='分组方式(city/area/location)，默认为area', type=openapi.TYPE_STRING, required=False),
            openapi.Parameter('limit', openapi.IN_QUERY, description='返回数据条数限制，默认为10', type=openapi.TYPE_INTEGER, required=False),
        ],
        responses={
            200: openapi.Response('成功获取统计数据'),
            400: openapi.Response('参数错误'),
            500: openapi.Response('服务器内部错误'),
        }
    )
    def get(self, request):
        try:
            city_id = request.query_params.get('city_id')
            group_by = request.query_params.get('group_by', 'area')  # 默认按区域分组
            limit = request.query_params.get('limit', 10)
            
            try:
                limit = int(limit)
            except (ValueError, TypeError):
                limit = 10
                
            # 初始化查询集
            queryset = city.objects.all()
            
            # 如果提供了城市ID，则过滤特定城市的数据
            if city_id and city_id.isdigit():
                queryset = queryset.filter(city_id=city_id)
            
            # 使用平均单价统计
            price_func = Avg('single_price')
            price_label = '平均单价'
            
            # 根据分组方式进行统计
            if group_by == 'city':
                # 按城市分组统计
                statistics = queryset.values('city_id', 'city_name')\
                    .annotate(price_value=price_func)\
                    .filter(price_value__isnull=False)\
                    .order_by('-price_value')[:limit]
                
                result = [
                    {
                        'name': item['city_name'],
                        'value': round(float(item['price_value']), 2) if item['price_value'] else 0,
                        'id': item['city_id']
                    } for item in statistics
                ]
                
            elif group_by == 'location':
                # 按具体位置分组统计
                statistics = queryset.values('localhost')\
                    .annotate(price_value=price_func)\
                    .filter(price_value__isnull=False)\
                    .order_by('-price_value')[:limit]
                
                result = [
                    {
                        'name': item['localhost'] or '未知位置',
                        'value': round(float(item['price_value']), 2) if item['price_value'] else 0
                    } for item in statistics
                ]
                
            else:  # 默认按区域分组
                # 按区域分组统计
                statistics = queryset.values('area_id')\
                    .annotate(price_value=price_func)\
                    .filter(price_value__isnull=False)\
                    .order_by('-price_value')[:limit]
                
                # 获取区域名称
                result = []
                for item in statistics:
                    area_obj = Area.objects.filter(id=item['area_id']).first()
                    area_name = area_obj.name if area_obj else '未知区域'
                    result.append({
                        'name': area_name,
                        'value': round(float(item['price_value']), 2) if item['price_value'] else 0
                    })
            
            return Response({
                'code': '200',
                'info': '获取成功',
                'data': result,
                'stat_type': price_label
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'code': '500',
                'info': f'服务器内部错误: {str(e)}',
                'data': []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HousePriceStatisticsView(APIView):
    authentication_classes = (
        SessionAuthentication,
        JWTAuthentication
    )
    
    @swagger_auto_schema(
        operation_summary='获取地区房源金额统计',
        operation_description='获取各地区房源平均价格统计，按金额从大到小排序',
        manual_parameters=[
            openapi.Parameter('city_id', openapi.IN_QUERY, description='城市ID(可选)', type=openapi.TYPE_INTEGER, required=False),
            openapi.Parameter('group_by', openapi.IN_QUERY, description='分组方式(city/area/location)，默认为area', type=openapi.TYPE_STRING, required=False),
            openapi.Parameter('limit', openapi.IN_QUERY, description='返回数据条数限制，默认为10', type=openapi.TYPE_INTEGER, required=False),
        ],
        responses={
            200: openapi.Response('成功获取统计数据'),
            400: openapi.Response('参数错误'),
            500: openapi.Response('服务器内部错误'),
        }
    )
    def get(self, request):
        try:
            city_id = request.query_params.get('city_id')
            group_by = request.query_params.get('group_by', 'area')  # 默认按区域分组
            limit = request.query_params.get('limit', 10)
            
            try:
                limit = int(limit)
            except (ValueError, TypeError):
                limit = 10
                
            # 初始化查询集
            queryset = city.objects.all()
            
            # 如果提供了城市ID，则过滤特定城市的数据
            if city_id and city_id.isdigit():
                queryset = queryset.filter(city_id=city_id)
            
            # 使用平均价格统计
            price_func = Avg('price')
            price_label = '平均价格'
            
            # 根据分组方式进行统计
            if group_by == 'city':
                # 按城市分组统计
                statistics = queryset.values('city_id', 'city_name')\
                    .annotate(price_value=price_func)\
                    .filter(price_value__isnull=False)\
                    .order_by('-price_value')[:limit]
                
                result = [
                    {
                        'name': item['city_name'],
                        'value': round(float(item['price_value']), 2) if item['price_value'] else 0,
                        'id': item['city_id']
                    } for item in statistics
                ]
                
            elif group_by == 'location':
                # 按具体位置分组统计
                statistics = queryset.values('localhost')\
                    .annotate(price_value=price_func)\
                    .filter(price_value__isnull=False)\
                    .order_by('-price_value')[:limit]
                
                result = [
                    {
                        'name': item['localhost'] or '未知位置',
                        'value': round(float(item['price_value']), 2) if item['price_value'] else 0
                    } for item in statistics
                ]
                
            else:  # 默认按区域分组
                # 按区域分组统计
                statistics = queryset.values('area_id')\
                    .annotate(price_value=price_func)\
                    .filter(price_value__isnull=False)\
                    .order_by('-price_value')[:limit]
                
                # 获取区域名称
                result = []
                for item in statistics:
                    area_obj = Area.objects.filter(id=item['area_id']).first()
                    area_name = area_obj.name if area_obj else '未知区域'
                    result.append({
                        'name': area_name,
                        'value': round(float(item['price_value']), 2) if item['price_value'] else 0
                    })
            
            return Response({
                'code': '200',
                'info': '获取成功',
                'data': result,
                'stat_type': price_label
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'code': '500',
                'info': f'服务器内部错误: {str(e)}',
                'data': []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class HouseAttributeStatisticsView(APIView):
    authentication_classes = (
        SessionAuthentication,
        JWTAuthentication
    )
    
    @swagger_auto_schema(
        operation_summary='获取房源属性统计',
        operation_description='获取房源楼层、装修、户型和朝向的数量分布，按数量从大到小排序',
        manual_parameters=[
            openapi.Parameter('city_id', openapi.IN_QUERY, description='城市ID(可选)', type=openapi.TYPE_INTEGER, required=False),
            openapi.Parameter('area_id', openapi.IN_QUERY, description='区域ID(可选)', type=openapi.TYPE_INTEGER, required=False),
            openapi.Parameter('attribute', openapi.IN_QUERY, description='统计属性(floor/fitment/type_name/forword)，默认为floor', type=openapi.TYPE_STRING, required=False),
            openapi.Parameter('limit', openapi.IN_QUERY, description='返回数据条数限制，默认为10', type=openapi.TYPE_INTEGER, required=False),
        ],
        responses={
            200: openapi.Response('成功获取统计数据'),
            400: openapi.Response('参数错误'),
            500: openapi.Response('服务器内部错误'),
        }
    )
    def get(self, request):
        try:
            city_id = request.query_params.get('city_id')
            area_id = request.query_params.get('area_id')
            attribute = request.query_params.get('attribute', 'floor')  # 默认统计楼层
            limit = request.query_params.get('limit', 10)
            
            try:
                limit = int(limit)
            except (ValueError, TypeError):
                limit = 10
                
            # 初始化查询集
            queryset = city.objects.all()
            
            # 应用过滤条件
            if city_id and city_id.isdigit():
                queryset = queryset.filter(city_id=city_id)
                
            if area_id and area_id.isdigit():
                queryset = queryset.filter(area_id=area_id)
            
            # 确保属性名有效
            valid_attributes = ['floor', 'fitment', 'type_name', 'forword']
            if attribute not in valid_attributes:
                attribute = 'floor'  # 默认为楼层
                
            # 获取属性的中文名称
            attribute_labels = {
                'floor': '楼层',
                'fitment': '装修',
                'type_name': '户型',
                'forword': '朝向'
            }
            
            # 进行统计
            statistics = queryset.values(attribute)\
                .annotate(count=Count('id'))\
                .filter(count__gt=0)\
                .order_by('-count')[:limit]
            
            result = [
                {
                    'name': item[attribute] or f'未知{attribute_labels[attribute]}',
                    'value': item['count']
                } for item in statistics
            ]
            
            return Response({
                'code': '200',
                'info': '获取成功',
                'data': result,
                'attribute': attribute_labels[attribute]
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'code': '500',
                'info': f'服务器内部错误: {str(e)}',
                'data': []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HouseCommunityStatisticsView(APIView):
    authentication_classes = (
        SessionAuthentication,
        JWTAuthentication
    )
    
    @swagger_auto_schema(
        operation_summary='获取城市各小区房源数量统计',
        operation_description='根据城市ID获取该城市下各小区的在售房源数量，按数量从大到小排序',
        manual_parameters=[
            openapi.Parameter('city_id', openapi.IN_QUERY, description='城市ID', type=openapi.TYPE_INTEGER, required=True),
            openapi.Parameter('limit', openapi.IN_QUERY, description='返回数据条数限制，默认为20', type=openapi.TYPE_INTEGER, required=False),
        ],
        responses={
            200: openapi.Response('成功获取统计数据'),
            400: openapi.Response('参数错误'),
            500: openapi.Response('服务器内部错误'),
        }
    )
    def get(self, request):
        try:
            city_id = request.query_params.get('city_id')
            limit = request.query_params.get('limit', 20)
            
            # 验证参数
            if not city_id or not city_id.isdigit():
                return Response({
                    'code': '400',
                    'info': '缺少有效的城市ID参数',
                    'data': []
                }, status=status.HTTP_400_BAD_REQUEST)
                
            try:
                limit = int(limit)
            except (ValueError, TypeError):
                limit = 20
                
            # 查询该城市下各小区的房源数量
            statistics = city.objects.filter(city_id=city_id)\
                .values('house_name')\
                .annotate(count=Count('id'))\
                .filter(count__gt=0)\
                .order_by('-count')[:limit]
            
            result = [
                {
                    'name': item['house_name'] or '未知小区',
                    'value': item['count']
                } for item in statistics
            ]
            
            return Response({
                'code': '200',
                'info': '获取成功',
                'data': result
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'code': '500',
                'info': f'服务器内部错误: {str(e)}',
                'data': []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HouseUpdateView(APIView):
    authentication_classes = (
        SessionAuthentication,
        JWTAuthentication
    )
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_summary='修改房源信息',
        operation_description='根据房源ID修改房源信息',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['id'],
            properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='房源ID'),
                'house_name': openapi.Schema(type=openapi.TYPE_STRING, description='小区名称'),
                'price': openapi.Schema(type=openapi.TYPE_NUMBER, description='总价'),
                'single_price': openapi.Schema(type=openapi.TYPE_NUMBER, description='单价'),
                'type_name': openapi.Schema(type=openapi.TYPE_STRING, description='户型'),
                'floor': openapi.Schema(type=openapi.TYPE_STRING, description='楼层'),
                'use_area': openapi.Schema(type=openapi.TYPE_NUMBER, description='面积'),
                'fitment': openapi.Schema(type=openapi.TYPE_STRING, description='装修'),
                'forword': openapi.Schema(type=openapi.TYPE_STRING, description='朝向'),
                'localhost': openapi.Schema(type=openapi.TYPE_STRING, description='具体位置'),
                'city_name': openapi.Schema(type=openapi.TYPE_STRING, description='区域名称'),
                'city_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='城市ID'),
                'area_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='区域ID'),
                'location_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='位置ID'),
            }
        ),
        responses={
            200: openapi.Response('修改成功'),
            400: openapi.Response('参数错误'),
            401: openapi.Response('未认证'),
            404: openapi.Response('房源不存在'),
            500: openapi.Response('服务器内部错误'),
        }
    )
    def put(self, request):
        try:
            data = request.data
            house_id = data.get('id')
            
            if not house_id:
                return Response({
                    'code': '400',
                    'info': '缺少房源ID',
                    'data': {}
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 查找房源
            house = city.objects.filter(id=house_id).first()
            if not house:
                return Response({
                    'code': '404',
                    'info': '房源不存在',
                    'data': {}
                }, status=status.HTTP_404_NOT_FOUND)
            
            # 更新房源信息
            update_fields = {}
            
            # 可更新的字段列表
            updatable_fields = [
                'house_name', 'price', 'single_price', 'type_name', 
                'floor', 'use_area', 'fitment', 'forword', 'localhost', 
                'city_name', 'city_id', 'area_id', 'location_id'
            ]
            
            # 检查并添加需要更新的字段
            for field in updatable_fields:
                if field in data and data[field] is not None:
                    update_fields[field] = data[field]
            
            # 如果没有需要更新的字段
            if not update_fields:
                return Response({
                    'code': '400',
                    'info': '没有提供需要更新的字段',
                    'data': {}
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 更新房源
            city.objects.filter(id=house_id).update(**update_fields)
            
            # 获取更新后的房源信息
            updated_house = city.objects.get(id=house_id)
            serializer = HouseSerializer(updated_house)
            
            return Response({
                'code': '200',
                'info': '房源信息修改成功',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'code': '500',
                'info': f'服务器内部错误: {str(e)}',
                'data': {}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        



class HouseClusterAnalysisView(APIView):
    authentication_classes = (
        SessionAuthentication,
        JWTAuthentication
    )
    
    @swagger_auto_schema(
        operation_summary='房屋聚类分析',
        operation_description='对房屋数据进行聚类分析，返回聚类结果',
        manual_parameters=[
            openapi.Parameter('city_id', openapi.IN_QUERY, description='城市ID(可选)', type=openapi.TYPE_INTEGER, required=False),
            openapi.Parameter('area_id', openapi.IN_QUERY, description='区域ID(可选)', type=openapi.TYPE_INTEGER, required=False),
            openapi.Parameter('n_clusters', openapi.IN_QUERY, description='聚类数量，默认为3', type=openapi.TYPE_INTEGER, required=False),
            # 更新默认特征列表和描述
            openapi.Parameter('features', openapi.IN_QUERY, description='用于聚类的特征，多个特征用逗号分隔，默认为price,single_price,use_area,floor,type_name,forword,fitment', type=openapi.TYPE_STRING, required=False),
            openapi.Parameter('limit', openapi.IN_QUERY, description='返回每个聚类的样本数量限制，默认为10', type=openapi.TYPE_INTEGER, required=False),
        ],
        responses={
            200: openapi.Response('成功获取聚类结果'),
            400: openapi.Response('参数错误'),
            500: openapi.Response('服务器内部错误'),
        }
    )
    def get(self, request):
        try:
            # 获取参数
            city_id = request.query_params.get('city_id')
            area_id = request.query_params.get('area_id')
            n_clusters = request.query_params.get('n_clusters', '3')
            # 默认包含新特征
            features_str = request.query_params.get('features', 'price,single_price,use_area,floor,type_name,forword,fitment')
            limit_per_cluster = request.query_params.get('limit', '10')
            
            try:
                n_clusters = int(n_clusters)
                if n_clusters < 2 or n_clusters > 10:
                    n_clusters = 3
            except (ValueError, TypeError):
                n_clusters = 3
                
            try:
                limit_per_cluster = int(limit_per_cluster)
                if limit_per_cluster < 1 or limit_per_cluster > 100:
                    limit_per_cluster = 10
            except (ValueError, TypeError):
                limit_per_cluster = 10
            
            # 解析特征列表
            requested_features = [f.strip() for f in features_str.split(',') if f.strip()]
            
            # 定义所有可能的有效特征和它们的类型
            all_valid_features_info = {
                'price': 'numeric',
                'single_price': 'numeric',
                'use_area': 'numeric',
                'floor': 'categorical', 
                'type_name': 'categorical',
                'forword': 'categorical',
                'fitment': 'categorical'
            }
            
            # 筛选出用户请求的有效特征
            valid_features = [f for f in requested_features if f in all_valid_features_info]
            
            # 如果没有有效特征，使用默认数值特征
            if not valid_features:
                valid_features = ['price', 'single_price', 'use_area']
            
            # 分离数值和分类特征
            numeric_features = [f for f in valid_features if all_valid_features_info[f] == 'numeric']
            categorical_features = [f for f in valid_features if all_valid_features_info[f] == 'categorical']

            # 初始化查询集
            queryset = city.objects.all()
            
            # 应用过滤条件
            if city_id and city_id.isdigit():
                queryset = queryset.filter(city_id=city_id)
            if area_id and area_id.isdigit():
                queryset = queryset.filter(area_id=area_id)
            
            # 确保有足够的数据进行聚类
            if queryset.count() < n_clusters * 2:
                return Response({
                    'code': '400',
                    'info': '数据量不足，无法进行聚类分析',
                    'data': []
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 提取所需数据，包括原始特征和ID等信息
            data_fields = ['id', 'house_name', 'city_name', 'localhost'] + valid_features
            data = list(queryset.values(*data_fields))
            
            # 转换为DataFrame
            df = pd.DataFrame(data)

            # 处理缺失值 (例如，用均值填充数值特征，用众数或特定值填充分类特征)
            for col in numeric_features:
                if df[col].isnull().any():
                    df[col].fillna(df[col].mean(), inplace=True)
            for col in categorical_features:
                if df[col].isnull().any():
                    # 填充为 '未知' 或最常见的类别
                    mode_val = df[col].mode()
                    fill_value = mode_val[0] if not mode_val.empty else '未知'
                    df[col].fillna(fill_value, inplace=True)
                    # 确保填充后的值是字符串类型，以便编码器处理
                    df[col] = df[col].astype(str)
            
            # 创建预处理管道
            preprocessor = ColumnTransformer(
                transformers=[
                    ('num', StandardScaler(), numeric_features),
                    ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), categorical_features)
                ],
                remainder='passthrough' # 保留其他列（如果需要）
            )

            # 应用预处理
            try:
                X_processed = preprocessor.fit_transform(df[valid_features])
                # 获取编码后的特征名称
                encoded_feature_names = preprocessor.get_feature_names_out()
            except ValueError as e:
                 # 如果分类特征只有单一值，OneHotEncoder会出错，这时可以考虑排除该特征或特殊处理
                 return Response({
                    'code': '400',
                    'info': f'特征预处理失败: {str(e)}. 可能某个分类特征只有单一值。',
                    'data': []
                }, status=status.HTTP_400_BAD_REQUEST)

            # 应用K-means聚类
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10) # 新版本n_init='auto'
            clusters = kmeans.fit_predict(X_processed)
            
            # 将聚类结果添加到DataFrame
            df['cluster'] = clusters
            
            # 计算每个聚类的中心点（在处理后的特征空间）
            cluster_centers_processed = kmeans.cluster_centers_

            # 计算每个聚类的统计信息 (在原始特征空间计算均值更有意义)
            cluster_centers_original = []
            for i in range(n_clusters):
                cluster_data = df[df['cluster'] == i]
                center = {}
                for feature in numeric_features:
                    center[feature] = float(cluster_data[feature].mean()) if not cluster_data.empty else 0
                # 对于分类特征，可以报告最常见的类别
                for feature in categorical_features:
                    mode_val = cluster_data[feature].mode()
                    center[feature] = mode_val[0] if not mode_val.empty else 'N/A'
                center['count'] = int(cluster_data.shape[0])
                center['cluster_id'] = i
                cluster_centers_original.append(center)
            
            # 对每个聚类，选择代表性样本
            cluster_samples = []
            for i in range(n_clusters):
                cluster_df = df[df['cluster'] == i]
                
                if cluster_df.empty:
                    continue

                # 如果聚类中的样本数量小于限制，则全部返回
                if cluster_df.shape[0] <= limit_per_cluster:
                    samples_df = cluster_df
                else:
                    # 计算到聚类中心(处理后空间)的距离
                    cluster_center_proc = cluster_centers_processed[i]
                    
                    # 获取该聚类处理后的特征
                    cluster_indices = cluster_df.index
                    X_cluster_processed = X_processed[cluster_indices]
                    
                    # 计算距离
                    distances = np.linalg.norm(X_cluster_processed - cluster_center_proc, axis=1)
                    
                    # 获取距离最近的样本的索引 (在原始df中的索引)
                    closest_indices_in_cluster = np.argsort(distances)[:limit_per_cluster]
                    closest_original_indices = cluster_df.iloc[closest_indices_in_cluster].index
                    samples_df = df.loc[closest_original_indices]
                
                # 转换为列表并添加到结果中
                for _, row in samples_df.iterrows():
                    sample_dict = {
                        'id': int(row['id']),
                        'house_name': row['house_name'],
                        'city_name': row['city_name'],
                        'localhost': row['localhost'],
                        'cluster_id': int(row['cluster'])
                    }
                    # 添加所有请求的原始特征值
                    for feature in valid_features:
                        # 数值特征转为 float，分类特征保持原样 (通常是字符串)
                        if feature in numeric_features:
                            sample_dict[feature] = float(row[feature]) if pd.notna(row[feature]) else None
                        else:
                            sample_dict[feature] = row[feature] # 保持原始分类值
                    cluster_samples.append(sample_dict)
            
            # 准备PCA降维结果用于可视化（在处理后的特征空间上进行）
            visualization_data = []
            if X_processed.shape[1] > 1: # 至少需要两个维度才能可视化
                if X_processed.shape[1] > 2:
                    pca = PCA(n_components=2)
                    X_pca = pca.fit_transform(X_processed)
                else: # 如果处理后刚好是2维，直接使用
                    X_pca = X_processed
                
                # 创建可视化数据
                for i in range(df.shape[0]): # 遍历所有原始数据点
                    original_index = df.index[i]
                    visualization_data.append({
                        'id': int(df.loc[original_index, 'id']),
                        'x': float(X_pca[i, 0]),
                        'y': float(X_pca[i, 1]),
                        'cluster_id': int(df.loc[original_index, 'cluster'])
                    })
            elif X_processed.shape[1] == 1: # 如果只有1维
                 for i in range(df.shape[0]):
                    original_index = df.index[i]
                    visualization_data.append({
                        'id': int(df.loc[original_index, 'id']),
                        'x': float(X_processed[i, 0]),
                        'y': 0.0, # Y轴设为0
                        'cluster_id': int(df.loc[original_index, 'cluster'])
                    })
            
            # 构建响应数据
            response_data = {
                'clusters': cluster_centers_original, # 返回基于原始特征计算的统计信息
                'samples': cluster_samples,
                'features': valid_features, # 返回用户请求的特征列表
                'visualization': visualization_data
            }
            
            # 添加一些统计信息到聚类中心描述中
            for cluster in cluster_centers_original:
                cluster['avg_price'] = cluster.get('price', 0)
                cluster['avg_area'] = cluster.get('use_area', 0)
                # 查找代表性房屋名称
                representative_sample = next((s for s in cluster_samples if s['cluster_id'] == cluster['cluster_id']), None)
                cluster['representative_house'] = representative_sample['house_name'] if representative_sample else 'N/A'
            
            return Response({
                'code': '200',
                'info': '聚类分析成功',
                'data': response_data,
                'features_used': valid_features, # 明确指出实际使用的特征
                'n_clusters': n_clusters
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            import traceback
            print(traceback.format_exc()) # 打印详细错误信息到服务器日志
            return Response({
                'code': '500',
                'info': f'服务器内部错误: {str(e)}',
                'data': []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
