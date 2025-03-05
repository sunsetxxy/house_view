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


from pyecharts.charts import Bar, Pie, Line
from pyecharts import options as opts
from django.http import HttpResponse
from pyecharts.globals import ThemeType
from django.db.models import Avg, Count


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

# 添加新的视图类
class HouseAnalysisView(APIView):
    authentication_classes = (
        SessionAuthentication,
        JWTAuthentication
    )

    def get(self, request):
        # 1. 各城市房屋均价
        city_avg_price = city.objects.values('city').annotate(
            avg_price=Avg('price'),
            count=Count('id')
        ).order_by('-avg_price')

        # 创建柱状图
        bar = Bar(init_opts=opts.InitOpts(theme=ThemeType.LIGHT))
        bar.add_xaxis([item['city'] for item in city_avg_price])
        bar.add_yaxis("平均房价(万元)", [round(item['avg_price'], 2) for item in city_avg_price])
        bar.set_global_opts(
            title_opts=opts.TitleOpts(title="各城市房屋均价"),
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=30)),
            tooltip_opts=opts.TooltipOpts(trigger="axis"),
        )

        # 2. 户型分布饼图
        type_distribution = city.objects.values('type_name').annotate(
            count=Count('id')
        ).order_by('-count')[:10]

        pie = Pie(init_opts=opts.InitOpts(theme=ThemeType.LIGHT))
        pie.add(
            series_name="户型分布",
            data_pair=[(item['type_name'], item['count']) for item in type_distribution],
            radius=["40%", "75%"],
        )
        pie.set_global_opts(
            title_opts=opts.TitleOpts(title="户型分布"),
            legend_opts=opts.LegendOpts(orient="vertical", pos_top="15%", pos_left="2%")
        )

        return JsonResponse({
            'code': '200',
            'info': '获取成功',
            'data': {
                'bar_chart': bar.dump_options(),
                'pie_chart': pie.dump_options()
            }
        })
        