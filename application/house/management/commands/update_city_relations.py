from django.core.management.base import BaseCommand
from house.models import city, city_id, Area, Location
from django.db import transaction

class Command(BaseCommand):
    help = '更新 city 表中的关联ID'

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                # 更新计数器
                updated_count = 0
                skipped_count = 0

                # 遍历所有 city 记录
                for city_record in city.objects.all():
                    try:
                        # 获取对应的 city_id
                        city_instance = city_id.objects.filter(city=city_record.city).first()
                        
                        if city_instance:
                            # 获取对应的 area_id
                            area = Area.objects.filter(
                                name=city_record.city_name,
                                city_id=city_instance.id
                            ).first()
                            
                            if area:
                                # 获取对应的 location_id
                                location = Location.objects.filter(
                                    location=city_record.localhost,
                                    area_id=area.id
                                ).first()
                                
                                if location:
                                    # 更新 city 记录
                                    city_record.city_id = city_instance.id
                                    city_record.area_id = area.id
                                    city_record.location_id = location.id
                                    city_record.save()
                                    updated_count += 1
                                    continue
                            
                        skipped_count += 1
                        
                    except Exception as e:
                        self.stdout.write(
                            self.style.WARNING(f'处理记录 {city_record.id} 时出错: {str(e)}')
                        )
                        skipped_count += 1

                self.stdout.write(
                    self.style.SUCCESS(
                        f'数据更新完成：\n'
                        f'成功更新记录：{updated_count}\n'
                        f'跳过的记录：{skipped_count}'
                    )
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'发生错误: {str(e)}')
            )