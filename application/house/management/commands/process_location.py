from django.core.management.base import BaseCommand
from house.models import city, Area, Location  # 修改为正确的模型名称
from django.db import transaction

class Command(BaseCommand):
    help = '处理位置数据并关联区域ID'

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                unique_locations = city.objects.values('localhost', 'city_name').distinct()
                
                created_count = 0
                skipped_count = 0
                
                for location_data in unique_locations:
                    localhost = location_data['localhost']
                    city_name = location_data['city_name']
                    
                    if localhost and city_name:
                        area = Area.objects.filter(name=city_name).first()
                        
                        if area:
                            # 使用正确的模型名称 Location
                            location, created = Location.objects.get_or_create(
                                location=localhost,
                                area_id=area.id
                            )
                            if created:
                                created_count += 1
                        else:
                            skipped_count += 1

                self.stdout.write(
                    self.style.SUCCESS(
                        f'位置数据处理完成：\n'
                        f'新创建的位置记录：{created_count}\n'
                        f'跳过的记录（未找到对应区域）：{skipped_count}'
                    )
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'发生错误: {str(e)}')
            )