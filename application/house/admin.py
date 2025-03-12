from django.contrib import admin
from .models import city, city_id, Area, Location

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
        ('基本信息', {
            'fields': ('house_name', 'city', 'city_name', 'localhost')
        }),
        ('价格信息', {
            'fields': ('price', 'single_price')
        }),
        ('房屋特性', {
            'fields': ('type_name', 'use_area', 'forword', 'floor', 'fitment')
        }),
        ('其他信息', {
            'fields': ('url', 'city_id', 'area_id', 'location_id')
        }),
    )

# 城市基础信息管理
@admin.register(city_id)
class CityIdAdmin(admin.ModelAdmin):
    list_display = ('id', 'city')
    search_fields = ('city',)

# 区域管理
@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'get_city_name')
    list_filter = ('city_id',)
    search_fields = ('name',)
    
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
