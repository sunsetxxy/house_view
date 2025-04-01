from django.contrib import admin
from .models import city, city_id, Area, Location
from django.utils.translation import gettext_lazy as _

# 城市房产信息管理
@admin.register(city)
class CityAdmin(admin.ModelAdmin):
    list_display = ('id', 'house_name', 'city', 'city_name', 'localhost', 'price', 'type_name', 'use_area', 'single_price')
    list_filter = ('city', 'city_name', 'fitment')
    search_fields = ('house_name', 'localhost')
    list_per_page = 20
    ordering = ('-price',)  # 默认按价格降序排列
    readonly_fields = ('url',)  # 网址字段设为只读
    fieldsets = (
        (_('基本信息'), {
            'fields': ('house_name', 'city', 'city_name', 'localhost'),
            'description': _('房产的基本信息，包括名称和位置')
        }),
        (_('价格信息'), {
            'fields': ('price', 'single_price'),
            'description': _('房产的价格相关信息')
        }),
        (_('房屋特性'), {
            'fields': ('type_name', 'use_area', 'forword', 'floor', 'fitment'),
            'description': _('房屋的物理特性和装修情况')
        }),
        (_('其他信息'), {
            'fields': ('url', 'city_id', 'area_id', 'location_id'),
            'description': _('房产的其他相关信息和关联ID')
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.order_by('-price')  # 默认按价格降序排列

# 城市基础信息管理
@admin.register(city_id)
class CityIdAdmin(admin.ModelAdmin):
    list_display = ('id', 'city')
    search_fields = ('city',)
    list_per_page = 20
    
    fieldsets = (
        (_('城市信息'), {
            'fields': ('city',),
            'description': _('城市基础信息')
        }),
    )

# 区域管理
@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'get_city_name')
    list_filter = ('city_id',)
    search_fields = ('name',)
    list_per_page = 20
    
    fieldsets = (
        (_('区域信息'), {
            'fields': ('name', 'city_id'),
            'description': _('区域基础信息及所属城市')
        }),
    )
    
    def get_city_name(self, obj):
        try:
            # 如果 city_id 是整数，则需要查询 city_id 对象
            city_instance = city_id.objects.get(id=obj.city_id)
            return city_instance.city
        except (city_id.DoesNotExist, AttributeError):
            return '-'
    get_city_name.short_description = '所属城市'
    get_city_name.admin_order_field = 'city_id__city'

# 位置管理
@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('id', 'location', 'get_area_name', 'get_city_name', 'get_house_count')
    list_filter = ('area_id',)
    search_fields = ('location',)
    list_per_page = 20
    
    fieldsets = (
        (_('位置信息'), {
            'fields': ('location', 'area_id'),
            'description': _('位置基础信息及所属区域')
        }),
    )
    
    def get_area_name(self, obj):
        try:
            # 如果 area_id 是整数，则需要查询 Area 对象
            area = Area.objects.get(id=obj.area_id)
            return area.name
        except (Area.DoesNotExist, AttributeError):
            return '-'
    get_area_name.short_description = '所属区域'
    
    def get_city_name(self, obj):
        try:
            # 先获取 Area 对象
            area = Area.objects.get(id=obj.area_id)
            # 再获取 city_id 对象
            city_instance = city_id.objects.get(id=area.city_id)
            return city_instance.city
        except (Area.DoesNotExist, city_id.DoesNotExist, AttributeError):
            return '-'
    get_city_name.short_description = '所属城市'
    
    def get_house_count(self, obj):
        return city.objects.filter(location_id=obj.id).count()
    get_house_count.short_description = '房源数量'
