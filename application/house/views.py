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
from sklearn.preprocessing import StandardScaler
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
            openapi.Parameter('features', openapi.IN_QUERY, description='用于聚类的特征，多个特征用逗号分隔，默认为price,single_price,use_area', type=openapi.TYPE_STRING, required=False),
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
            features_str = request.query_params.get('features', 'price,single_price,use_area')
            limit_per_cluster = request.query_params.get('limit', '10')
            
            try:
                n_clusters = int(n_clusters)
                if n_clusters < 2 or n_clusters > 10:
                    n_clusters = 3  # 默认值，避免极端值
            except (ValueError, TypeError):
                n_clusters = 3
                
            try:
                limit_per_cluster = int(limit_per_cluster)
                if limit_per_cluster < 1 or limit_per_cluster > 100:
                    limit_per_cluster = 10
            except (ValueError, TypeError):
                limit_per_cluster = 10
            
            # 解析特征列表
            features = features_str.split(',')
            valid_features = []
            
            # 验证特征是否有效
            all_valid_features = ['price', 'single_price', 'use_area']
            for feature in features:
                feature = feature.strip()
                if feature in all_valid_features:
                    valid_features.append(feature)
            
            # 如果没有有效特征，使用默认特征
            if not valid_features:
                valid_features = ['price', 'single_price', 'use_area']
            
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
            
            # 提取特征数据
            data = list(queryset.values('id', 'house_name', 'city_name', 'localhost', *valid_features))
            
            # 转换为DataFrame
            df = pd.DataFrame(data)
            
            # 提取特征矩阵
            X = df[valid_features].values
            
            # 标准化特征
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # 应用K-means聚类
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            clusters = kmeans.fit_predict(X_scaled)
            
            # 将聚类结果添加到DataFrame
            df['cluster'] = clusters
            
            # 计算每个聚类的中心点（原始特征空间）
            cluster_centers = []
            for i in range(n_clusters):
                cluster_data = df[df['cluster'] == i]
                center = {}
                for feature in valid_features:
                    center[feature] = float(cluster_data[feature].mean())
                center['count'] = int(cluster_data.shape[0])
                center['cluster_id'] = i
                cluster_centers.append(center)
            
            # 对每个聚类，选择代表性样本
            cluster_samples = []
            for i in range(n_clusters):
                cluster_df = df[df['cluster'] == i]
                
                # 如果聚类中的样本数量小于限制，则全部返回
                if cluster_df.shape[0] <= limit_per_cluster:
                    samples = cluster_df
                else:
                    # 计算到聚类中心的距离
                    cluster_center = kmeans.cluster_centers_[i]
                    
                    # 为每个样本计算到中心的距离
                    distances = []
                    for idx, row in cluster_df.iterrows():
                        sample_features = [row[feature] for feature in valid_features]
                        sample_features_scaled = scaler.transform([sample_features])[0]
                        distance = np.linalg.norm(sample_features_scaled - cluster_center)
                        distances.append((idx, distance))
                    
                    # 按距离排序，选择最接近中心的样本
                    distances.sort(key=lambda x: x[1])
                    closest_indices = [x[0] for x in distances[:limit_per_cluster]]
                    samples = cluster_df.loc[closest_indices]
                
                # 转换为列表并添加到结果中
                for _, row in samples.iterrows():
                    sample_dict = {
                        'id': int(row['id']),
                        'house_name': row['house_name'],
                        'city_name': row['city_name'],
                        'localhost': row['localhost'],
                        'cluster_id': int(row['cluster'])
                    }
                    for feature in valid_features:
                        sample_dict[feature] = float(row[feature])
                    cluster_samples.append(sample_dict)
            
            # 准备PCA降维结果用于可视化（如果特征数量大于2）
            visualization_data = None
            if len(valid_features) > 2:
                pca = PCA(n_components=2)
                X_pca = pca.fit_transform(X_scaled)
                
                # 创建可视化数据
                visualization_data = []
                for i, (x, y) in enumerate(X_pca):
                    visualization_data.append({
                        'id': int(df.iloc[i]['id']),
                        'x': float(x),
                        'y': float(y),
                        'cluster_id': int(clusters[i])
                    })
            
            # 构建响应数据
            response_data = {
                'clusters': cluster_centers,
                'samples': cluster_samples,
                'features': valid_features,
                'visualization': visualization_data
            }
            
            # 确保总是返回visualization字段
            visualization_data = []
            if len(valid_features) > 2:
                pca = PCA(n_components=2)
                X_pca = pca.fit_transform(X_scaled)
                for i, (x, y) in enumerate(X_pca):
                    visualization_data.append({
                        'id': int(df.iloc[i]['id']),
                        'x': float(x),
                        'y': float(y),
                        'cluster_id': int(clusters[i])
                    })
            else:
                # 当特征数量<=2时，直接使用标准化后的特征值作为坐标
                for i in range(len(X_scaled)):
                    visualization_data.append({
                        'id': int(df.iloc[i]['id']),
                        'x': float(X_scaled[i][0]),
                        'y': float(X_scaled[i][1]) if len(valid_features) > 1 else 0,
                        'cluster_id': int(clusters[i])
                    })
            
            # 添加聚类统计信息
            for cluster in cluster_centers:
                cluster['avg_price'] = cluster.get('price', 0)
                cluster['avg_area'] = cluster.get('use_area', 0)
                cluster['representative_house'] = next(
                    (s['house_name'] for s in cluster_samples if s['cluster_id'] == cluster['cluster_id']),
                    ''
                )
            
            return Response({
                'code': '200',
                'info': '聚类分析成功',
                'data': response_data,
                'features': valid_features,
                'n_clusters': n_clusters
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
        