from django.core.management.base import BaseCommand
from house.models import city_id

class Command(BaseCommand):
    help = '插入初始城市数据'

    def handle(self, *args, **options):
        cities = ['北京', '上海', '重庆', '杭州']
        count = 0

        for city_name in cities:
            try:
                _, created = city_id.objects.get_or_create(city=city_name)
                if created:
                    count += 1
                    self.stdout.write(self.style.SUCCESS(f'成功插入城市: {city_name}'))
                else:
                    self.stdout.write(self.style.WARNING(f'城市已存在: {city_name}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'插入城市 {city_name} 时出错: {str(e)}'))

        self.stdout.write(self.style.SUCCESS(f'完成! 成功插入 {count} 个城市'))