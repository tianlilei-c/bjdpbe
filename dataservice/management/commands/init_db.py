from django.core.management.base import BaseCommand
import pymongo
from django.conf import settings

class Command(BaseCommand):
    help = '初始化MongoDB数据库，清除现有集合并重新创建索引'

    def handle(self, *args, **options):
        # 连接MongoDB
        client = pymongo.MongoClient(
            host=settings.MONGODB_SETTINGS['host'],
            port=settings.MONGODB_SETTINGS['port']
        )
        
        db_name = settings.MONGODB_SETTINGS['db']
        db = client[db_name]
        
        # 检查连接状态
        try:
            client.admin.command('ping')
            self.stdout.write(self.style.SUCCESS('MongoDB连接成功'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'MongoDB连接失败: {e}'))
            return
        
        try:
            # 删除sensor_data集合（如果存在）
            if 'sensor_data' in db.list_collection_names():
                # 先删除集合中的索引
                indexes = list(db.sensor_data.list_indexes())
                for index in indexes:
                    if index['name'] != '_id_':  # 不删除主键索引
                        db.sensor_data.drop_index(index['name'])
                        self.stdout.write(self.style.SUCCESS(f'已删除索引: {index["name"]}'))
                
                # 然后删除集合
                db.sensor_data.drop()
                self.stdout.write(self.style.SUCCESS('已删除sensor_data集合'))
            
            # 创建集合和索引
            db.create_collection('sensor_data')
            db.sensor_data.create_index(
                [('timestamp', pymongo.ASCENDING)], 
                expireAfterSeconds=94608000,  # 3年 = 3*365*24*60*60秒
                name='timestamp_1',
                background=True
            )
            
            self.stdout.write(self.style.SUCCESS('成功初始化MongoDB数据库和索引'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'初始化数据库失败: {e}'))
        finally:
            client.close() 