from django.db import models

# Create your models here.
class city(models.Model):
    # ['小区名称','所在市','具体位置','房屋总价','户型','占地','单价','朝向','楼层','装修','网址']
    id = models.AutoField(primary_key=True)
    house_name = models.CharField(max_length=128, verbose_name='小区名称', help_text='小区名称')
    city_name = models.CharField(max_length=128, verbose_name='所在区', help_text='所在区')
    localhost = models.CharField(max_length=128, verbose_name='具体位置', help_text='具体位置')
    price = models.IntegerField(verbose_name='房屋总价', help_text='房屋总价(万元)')
    type_name = models.CharField(max_length=128, verbose_name='户型', help_text='户型')
    use_area = models.FloatField(verbose_name='占地面积', help_text='占地面积(平方米)')
    single_price = models.IntegerField(verbose_name='单价', help_text='单价(元/平方米)')
    forword = models.CharField(max_length=128, verbose_name='朝向', help_text='房屋朝向')
    floor = models.CharField(max_length=128, verbose_name='楼层', help_text='所在楼层')
    fitment = models.CharField(max_length=128, verbose_name='装修', help_text='装修情况')
    url = models.CharField(max_length=128, verbose_name='网址', help_text='房源链接')
    city = models.CharField(max_length=128, verbose_name='城市', help_text='所在城市')
    city_id = models.IntegerField(verbose_name='城市ID', help_text='关联城市ID', null=True, blank=True)
    area_id = models.IntegerField(verbose_name='区域ID', help_text='关联区域ID', null=True, blank=True)
    location_id = models.IntegerField(verbose_name='位置ID', help_text='关联位置ID', null=True, blank=True)

    class Meta:
        db_table = "city"
        verbose_name = "房产信息"
        verbose_name_plural = verbose_name

class city_id(models.Model):
    id = models.AutoField(primary_key=True)
    city = models.CharField(max_length=128, verbose_name='城市', help_text='城市名称')

    class Meta:
        db_table = "city_id"
        verbose_name = "城市信息"
        verbose_name_plural = verbose_name

class Area(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128, verbose_name='区域名称', help_text='区域名称')
    city_id = models.IntegerField(verbose_name='城市ID', help_text='关联的城市ID')

    class Meta:
        db_table = "area_id"
        verbose_name = "区域信息"
        verbose_name_plural = verbose_name
    
class Location(models.Model):
    id = models.AutoField(primary_key=True)
    location = models.CharField(max_length=128, verbose_name='位置', help_text='具体位置名称')
    area_id = models.IntegerField(verbose_name='区域ID', help_text='关联的区域ID')

    class Meta:
        db_table = "location_id"
        verbose_name = "位置信息"
        verbose_name_plural = verbose_name


