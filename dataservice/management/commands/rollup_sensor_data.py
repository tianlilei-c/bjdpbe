from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from typing import List, Dict

from mongoengine.connection import get_db


class Command(BaseCommand):
    help = "按分钟/小时/日将 sensor_data 增量汇总到对应集合（sensor_data_minute/hour/day）"

    def add_arguments(self, parser):
        parser.add_argument('--granularity', type=str, choices=['minute', 'hour', 'day'], default='minute', help='汇总粒度')
        parser.add_argument('--hours', type=int, default=24, help='回溯的小时数，用于本次增量聚合的时间窗口')
        parser.add_argument('--start', type=str, help='开始时间，ISO格式，如 2025-08-01T00:00:00Z')
        parser.add_argument('--end', type=str, help='结束时间，ISO格式，如 2025-08-02T00:00:00Z')

    def handle(self, *args, **options):
        granularity: str = options['granularity']
        start_iso: str = options.get('start')
        end_iso: str = options.get('end')
        hours: int = options['hours']

        if start_iso and end_iso:
            start_dt = datetime.fromisoformat(start_iso.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end_iso.replace('Z', '+00:00'))
        else:
            end_dt = timezone.now()
            start_dt = end_dt - timedelta(hours=hours)

        db = get_db()
        source = db['sensor_data']

        target_name = {
            'minute': 'sensor_data_minute',
            'hour': 'sensor_data_hour',
            'day': 'sensor_data_day',
        }[granularity]
        target = db[target_name]

        # 确保目标集合上有索引
        target.create_index('timestamp', name='ts_asc')
        target.create_index([('timestamp', -1)], name='ts_desc')

        # 选取常用指标做示范，可按需扩展
        avg_fields: List[str] = [
            'FEED_T_HG', 'FEED_T_STC', 'FEED_T_NH',
            'BACK_T_HG', 'BACK_T_STC', 'BACK_T_NH',
            'FEED_P_HG', 'FEED_P_STC', 'FEED_P_NH',
            'BACK_P_HG', 'BACK_P_STC', 'BACK_P_NH',
        ]
        sum_fields: List[str] = [
            'U1_FLOW', 'U2_FLOW', 'U3_FLOW', 'U4_FLOW', 'U5_FLOW', 'U6_FLOW', 'U7_FLOW', 'U8_FLOW',
            'F_STEAM_FLOW', 'F_DRAIN_FLOW'
        ]

        # $dateTrunc 单位
        unit = granularity

        pipeline = [
            {
                '$match': {
                    'timestamp': {'$gte': start_dt, '$lt': end_dt}
                }
            },
            {
                '$set': {
                    't_bucket': {
                        '$dateTrunc': {
                            'date': '$timestamp',
                            'unit': unit
                        }
                    }
                }
            },
            {
                '$group': self._build_group_stage(avg_fields, sum_fields)
            },
            {
                '$set': {'timestamp': '$_id'}
            },
            {
                '$unset': ['_id']
            },
            {
                '$merge': {
                    'into': target_name,
                    'on': 'timestamp',
                    'whenMatched': 'replace',
                    'whenNotMatched': 'insert'
                }
            }
        ]

        result = list(source.aggregate(pipeline, allowDiskUse=True))
        self.stdout.write(self.style.SUCCESS(f'{granularity} 汇总完成: 写入/更新 {len(result)} 条 [ {start_dt.isoformat()} , {end_dt.isoformat()} )'))

    def _build_group_stage(self, avg_fields: List[str], sum_fields: List[str]) -> Dict:
        group = {
            '_id': '$t_bucket'
        }
        for f in avg_fields:
            group[f + '_avg'] = {'$avg': f'${f}'}
        for f in sum_fields:
            group[f + '_sum'] = {'$sum': f'${f}'}
        return group


