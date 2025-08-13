from datetime import datetime, timedelta
from typing import Iterable, List, Optional

from mongoengine.queryset.visitor import Q

from .models import SensorData


def get_latest(fields: Optional[List[str]] = None):
    """
    读取最新一条记录，可选仅返回部分字段
    """
    qs = SensorData.objects.order_by('-timestamp')
    if fields:
        qs = qs.only(*(['timestamp'] + fields))
    return qs.first()


def choose_collection_by_span(start: datetime, end: datetime) -> str:
    """根据跨度选择汇总集合名"""
    span = end - start
    # < 2 天：分钟级；< 90 天：小时级；否则：日级
    if span <= timedelta(days=2):
        return 'sensor_data_minute'
    if span <= timedelta(days=90):
        return 'sensor_data_hour'
    return 'sensor_data_day'


def get_timeseries(start: datetime, end: datetime, fields: List[str], order: str = 'asc') -> List[dict]:
    """
    在[start, end) 区间按时间返回指定字段的时序数据，自动根据跨度选择分钟/小时/日汇总集合。
    返回字典列表：{ timestamp, field1, field2, ... }
    """
    from mongoengine.connection import get_db

    db = get_db()
    coll_name = choose_collection_by_span(start, end)
    coll = db[coll_name]

    projection = {f + '_avg': 1 for f in fields}
    projection['timestamp'] = 1

    cursor = coll.find(
        {'timestamp': {'$gte': start, '$lt': end}},
        projection
    ).sort('timestamp', 1 if order == 'asc' else -1)

    # 将汇总字段名改回原字段名，便于前端统一处理
    results: List[dict] = []
    for doc in cursor:
        item = {'timestamp': doc['timestamp']}
        for f in fields:
            item[f] = doc.get(f + '_avg')
        results.append(item)
    return results


