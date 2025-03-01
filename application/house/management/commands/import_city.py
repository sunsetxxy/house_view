from django.core.management.base import BaseCommand
import csv
import os
from django.conf import settings
from house.models import city  # 确保模型字段与清洗后的数据匹配


class Command(BaseCommand):
    help = '从CSV文件导入城市房产数据'

    def import_cities_from_csv(self, csv_file_path, city_name, batch_size=1000):
        success_count = 0
        error_count = 0
        objs = []
        
        try:
            with open(csv_file_path, 'r', encoding='utf-8-sig') as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    try:
                        # 清洗和转换每个字段
                        cleaned_data = {
                            'house_name': row['小区名称'].strip(),
                            'city_name': row['所在市'].strip(),
                            'localhost': row['具体位置'].strip(),
                            # 处理数值型字段（带单位转换）
                            'price': float(row['房屋总价'].strip().replace('万', '')),
                            'type_name': row['户型'].strip(),
                            'use_area': float(row['占地'].strip().replace('平米', '')),
                            'single_price': row['单价'].strip().split('元/平米')[0],
                            'forword': row['朝向'].strip(),
                            'floor': row['楼层'].strip(),
                            'fitment': row['装修'].strip(),
                            'url': row['网址'].strip(),
                            'city': city_name  # 确保模型中有对应字段
                        }
                        
                        objs.append(city(**cleaned_data))
                        
                        # 批量插入
                        if len(objs) >= batch_size:
                            city.objects.bulk_create(objs)
                            success_count += len(objs)
                            objs = []
                            
                    except (KeyError, ValueError, AttributeError) as e:
                        print(f"数据解析失败: {row}，错误: {str(e)}")
                        error_count += 1
                        continue
                        
                # 插入剩余数据
                if objs:
                    city.objects.bulk_create(objs)
                    success_count += len(objs)
                    
        except FileNotFoundError:
            print(f"文件未找到: {csv_file_path}")
            return (0, 0)
        
        print(f"成功插入 {success_count} 条，失败 {error_count} 条")
        return (success_count, error_count)


    def handle(self, *args, **options):
        city_mapping = {
                'beijing': '北京',
                'shanghai': '上海',
                'chongqing': '重庆',
                'hangzhou': '杭州'
            }
        
        for city_slug, city_name in city_mapping.items():
            csv_file_path = os.path.join(settings.BASE_DIR, 'pachong', f'{city_slug}.csv')
            
            if not os.path.exists(csv_file_path):
                self.stdout.write(self.style.WARNING(f"跳过 {city_name}，文件不存在: {csv_file_path}"))
                continue
                
            self.stdout.write(f"正在导入 {city_name} 数据...")
            success, errors = self.import_cities_from_csv(csv_file_path, city_name)
            self.stdout.write(
                self.style.SUCCESS(f"完成 {city_name}: 成功 {success} 条，失败 {errors} 条")
            )
