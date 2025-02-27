from django.db import models

# Create your models here.
class city(models.Model):
    # ['小区名称','所在市','具体位置','房屋总价','户型','占地','单价','朝向','楼层','装修','网址']
    id = models.AutoField(primary_key=True)
    house_name = models.CharField(max_length=128,verbose_name='小区名称',help_text='小区名称')
    city_name = models.CharField(max_length=128,verbose_name='所在区',help_text='所在区')
    localhost = models.CharField(max_length=128,verbose_name='具体位置',help_text='具体位置')
    price = models.IntegerField(verbose_name='房屋总价',help_text='房屋总价')
    type_name = models.CharField(max_length=128,verbose_name='户型',help_text='户型')
    use_area = models.FloatField(verbose_name='占地',help_text='占地')
    single_price = models.IntegerField(verbose_name='单价',help_text='单价')
    forword = models.CharField(max_length=128,verbose_name='朝向',help_text='朝向')
    floor = models.CharField(max_length=128,verbose_name='楼层',help_text='楼层')
    fitment = models.CharField(max_length=128,verbose_name='装修',help_text='装修')
    url = models.CharField(max_length=128,verbose_name='网址',help_text='网址')
    city = models.CharField(max_length=128,verbose_name='城市',help_text='城市')

    class Meta:
        db_table = "city"