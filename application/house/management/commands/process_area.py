from django.core.management.base import BaseCommand
from house.models import city, city_id, Area
from django.db import transaction

class Command(BaseCommand):
    help = '处理城市和区域数据'

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                # 处理城市数据
                unique_cities = city.objects.values('city').distinct()
                city_count = 0
                for city_data in unique_cities:
                    city_name = city_data['city']
                    if city_name:
                        _, created = city_id.objects.get_or_create(city=city_name)
                        if created:
                            city_count += 1

                # 处理区域数据
                unique_areas = city.objects.values('city_name', 'city').distinct()
                area_count = 0
                for area_data in unique_areas:
                    area_name = area_data['city_name']
                    city_name = area_data['city']
                    if area_name and city_name:
                        city_instance = city_id.objects.filter(city=city_name).first()
                        if city_instance:
                            _, created = Area.objects.get_or_create(
                                name=area_name,
                                city_id=city_instance.id
                            )
                            if created:
                                area_count += 1

                self.stdout.write(
                    self.style.SUCCESS(
                        f'数据处理完成：\n'
                        f'新增城市数：{city_count}\n'
                        f'新增区域数：{area_count}'
                    )
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'发生错误: {str(e)}')
            )