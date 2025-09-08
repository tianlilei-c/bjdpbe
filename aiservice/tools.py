# apps/aiservice/tools.py
import json
import datetime as dt
from typing import Any, Dict, List, Optional
from django.conf import settings
from pymongo import MongoClient
from pymongo.errors import PyMongoError

# 使用现有的MongoEngine连接，但这里用pymongo进行聚合查询
from mongoengine import connect
from dataservice.models import SensorData

class ToolError(Exception):
    pass

# 数据字段分类配置
SENSOR_FIELD_CATEGORIES = {
    "负荷": ["LDC_1", "LDC_2", "LDC_3", "LDC_4"],
    "五抽压力": ["S5_01", "S5_02", "S5_0301", "S5_0302", "S5_0401", "S5_0402"],
    "累计热量": ["HEATSUP_TOTAL_HG", "HEATSUP_TOTAL_STC", "HEATSUP_TOTAL_NH", "STEAMSUP_TOTAL_YC"],
    "供水流量": ["FEED_FLOW_HG", "FEED_FLOW_STC", "FEED_FLOW_NH"],
    "回水流量": ["BACK_FLOW_HG", "BACK_FLOW_STC", "BACK_FLOW_NH"],
    "供水压力": ["FEED_P_HG", "FEED_P_STC", "FEED_P_NH"],
    "回水压力": ["BACK_P_HG", "BACK_P_STC", "BACK_P_NH"],
    "实时热量": ["HEATNOW_HG", "HEATNOW_STC", "HEATNOW_NH"],
    "供水温度": ["FEED_T_HG", "FEED_T_STC", "FEED_T_NH"],
    "回水温度": ["BACK_T_HG", "BACK_T_STC", "BACK_T_NH"],
    "疏水流量": ["DRAIN_BH_03", "DRAIN_BH_04", "DRAIN_NH_03", "DRAIN_NH_04"],
    "补水流量": ["MAKEUP_BH_N", "MAKEUP_BH_E", "MAKEUP_NH_N", "MAKEUP_NH_E"],
    "海淡抽汽": ["U1_FLOW", "U2_FLOW", "U3_FLOW", "U4_FLOW", "U5_FLOW", "U6_FLOW", "U7_FLOW", "U8_FLOW"]
}

FIELD_DESCRIPTIONS = {
    "timestamp": "数据采集时间戳（10秒间隔）",
    "LDC_1": "1号机组负荷(MW)",
    "LDC_2": "2号机组负荷(MW)", 
    "LDC_3": "3号机组负荷(MW)",
    "LDC_4": "4号机组负荷(MW)",
    "S5_01": "1号机五抽压力(MPa)",
    "S5_02": "2号机五抽压力(MPa)",
    "S5_0301": "3号机五抽一路压力(MPa)",
    "S5_0302": "3号机五抽二路压力(MPa)",
    "S5_0401": "4号机五抽一路压力(MPa)",
    "S5_0402": "4号机五抽二路压力(MPa)",
    "HEATSUP_TOTAL_HG": "汉沽累计热量",
    "HEATSUP_TOTAL_STC": "生态城累计热量",
    "HEATSUP_TOTAL_NH": "宁河累计热量",
    "FEED_T_HG": "汉沽供水温度(°C)",
    "FEED_T_STC": "生态城供水温度(°C)",
    "FEED_T_NH": "宁河供水温度(°C)",
    "BACK_T_HG": "汉沽回水温度(°C)",
    "BACK_T_STC": "生态城回水温度(°C)",
    "BACK_T_NH": "宁河回水温度(°C)"
}

def coerce_time_range(tr: Optional[Dict[str, str]]) -> Dict[str, dt.datetime]:
    """
    将输入时间统一解释为北京时间（UTC+8），并返回无时区信息的 datetime（与现有存储一致）。

    规则：
    - 未提供 time_range：使用“当前北京时间”往前 24 小时
    - 提供 ISO 字符串且带 Z/时区偏移：先转为对应时区 → 再换算到北京时间 → 去掉 tzinfo
    - 提供无时区的字符串：按北京时间本地时间解释 → 去掉 tzinfo（保持原样）
    - 最终返回的 start/end 均为“北京时间的 naive datetime”，与现有存储匹配
    """
    tz_bj = dt.timezone(dt.timedelta(hours=8))

    def _parse_to_bj_naive(s: str) -> dt.datetime:
        d = None
        # 兼容 Z 结尾
        if "Z" in s:
            d = dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
        else:
            # 可能包含 +08:00/-xx:xx 偏移，或无偏移
            try:
                d = dt.datetime.fromisoformat(s)
            except Exception as e:
                raise ToolError(f"Invalid datetime format: {s}")

        # 有 tzinfo：换算到北京时间并去 tz
        if getattr(d, 'tzinfo', None) is not None:
            d = d.astimezone(tz_bj).replace(tzinfo=None)
        # 无 tzinfo：按北京时间本地时间对待
        return d

    if not tr:
        # 使用“当前北京时间”
        end_bj = (dt.datetime.utcnow().replace(tzinfo=dt.timezone.utc)).astimezone(tz_bj).replace(tzinfo=None)
        start_bj = end_bj - dt.timedelta(hours=24)
        return {"start": start_bj, "end": end_bj}

    try:
        start_str = (tr or {}).get("start")
        end_str = (tr or {}).get("end")
        if not start_str or not end_str:
            raise ToolError("time_range must contain both 'start' and 'end'")

        start = _parse_to_bj_naive(start_str)
        end = _parse_to_bj_naive(end_str)

        if start >= end:
            raise ToolError("start time must be before end time")

        # 限制最大时间范围
        max_hours = getattr(settings, 'AGENT_MAX_TIME_RANGE_HOURS', 72)
        if (end - start).total_seconds() > max_hours * 3600:
            start = end - dt.timedelta(hours=max_hours)

        return {"start": start, "end": end}
    except Exception as e:
        raise ToolError(f"Invalid time_range format: {str(e)}. Use ISO format like '2025-09-07T11:40:13.868Z'")

def ensure_collection_allowed(name: str):
    allowed = getattr(settings, 'AGENT_ALLOWED_COLLECTIONS', ['sensor_data'])
    if name not in allowed:
        raise ToolError(f"Collection '{name}' is not allowed.")

def describe_schema(collection: Optional[str] = None) -> Dict[str, Any]:
    allowed = getattr(settings, 'AGENT_ALLOWED_COLLECTIONS', ['sensor_data'])
    if collection:
        ensure_collection_allowed(collection)
        
        if collection == "sensor_data":
            # 针对传感器数据，返回字段分类和描述信息
            field_categories = SENSOR_FIELD_CATEGORIES
            
            # 取最新一条数据作为示例
            try:
                sample = SensorData.objects().order_by('-timestamp').limit(1).first()
                sample_dict = sample.to_mongo().to_dict() if sample else {}
                # 转换ObjectId为字符串
                if '_id' in sample_dict:
                    sample_dict['_id'] = str(sample_dict['_id'])
                if 'timestamp' in sample_dict:
                    sample_dict['timestamp'] = sample_dict['timestamp'].isoformat()
            except Exception as e:
                sample_dict = {"error": f"Failed to get sample: {str(e)}"}
            
            return {
                "collection": collection,
                "time_field": "timestamp",
                "sample_interval": "10秒采集一次",
                "field_categories": field_categories,
                "field_descriptions": FIELD_DESCRIPTIONS,
                "sample": [sample_dict] if sample_dict else [],
                "total_fields": len(sample_dict) if sample_dict and 'error' not in sample_dict else 0,
                "note": "高频数据，建议使用聚合查询以提升性能"
            }
        else:
            return {"collection": collection, "note": "Collection not fully supported yet"}
            
    return {"collections": allowed}

def run_aggregation(
    collection: str,
    pipeline: List[Dict[str, Any]],
    limit: int = 1000,
    projection: Optional[Dict[str, int]] = None,
    time_range: Optional[Dict[str, str]] = None,
    time_field: str = "timestamp",
    sample_interval: Optional[int] = None
) -> Dict[str, Any]:
    ensure_collection_allowed(collection)
    if not isinstance(pipeline, list):
        raise ToolError("pipeline must be a list of stages")

    # 强制 limit 上限（针对高频数据降低默认值）
    max_docs = getattr(settings, 'AGENT_MAX_DOCS', 5000)
    limit = min(limit or 1000, max_docs)
    tr = coerce_time_range(time_range)

    # 使用MongoEngine的底层连接进行聚合查询
    try:
        if collection == "sensor_data":
            # 1) 强制注入由后端控制的时间过滤（北京时间 naive datetime）
            final_pipeline: List[Dict[str, Any]] = [
                {"$match": {time_field: {"$gte": tr["start"], "$lte": tr["end"]}}}
            ]

            # 2) 清理用户管道中对 timestamp 的字符串/自定义匹配，避免与后端冲突
            sanitized_pipeline: List[Dict[str, Any]] = []
            for stage in pipeline:
                if not isinstance(stage, dict):
                    sanitized_pipeline.append(stage)
                    continue
                if "$match" in stage and isinstance(stage["$match"], dict):
                    match_body = stage["$match"]
                    # 删除所有直接作用于 time_field 的匹配，由后端统一处理
                    if time_field in match_body:
                        new_match = {k: v for k, v in match_body.items() if k != time_field}
                        if new_match:
                            sanitized_pipeline.append({"$match": new_match})
                        # 仅包含时间时，整段跳过
                        continue
                sanitized_pipeline.append(stage)

            # 自动数据采样：对于高频数据（10秒采集），自动按5分钟采样
            time_span_seconds = (tr["end"] - tr["start"]).total_seconds()
            estimated_records = int(time_span_seconds / 10)  # 10秒采集一次

            # 如果预估记录数超过50条，自动进行5分钟级采样
            if estimated_records > 50:
                # 在分组前按时间升序排序，确保 $first 语义稳定
                # 仅当用户未显式排序时添加
                has_user_sort = any(isinstance(st, dict) and "$sort" in st for st in sanitized_pipeline)
                if not has_user_sort:
                    final_pipeline.append({"$sort": {time_field: 1}})
                # 计算5分钟间隔的分钟数（0, 5, 10, 15, ...）
                sample_stage = {
                    "$group": {
                        "_id": {
                            "year": {"$year": f"${time_field}"},
                            "month": {"$month": f"${time_field}"},
                            "day": {"$dayOfMonth": f"${time_field}"},
                            "hour": {"$hour": f"${time_field}"},
                            "minute_group": {
                                "$subtract": [
                                    {"$minute": f"${time_field}"},
                                    {"$mod": [{"$minute": f"${time_field}"}, 5]}
                                ]
                            }
                        },
                        "doc": {"$first": "$$ROOT"}  # 取该5分钟间隔的第一条记录
                    }
                }
                final_pipeline.append(sample_stage)

                # 恢复文档结构
                replace_stage = {
                    "$replaceRoot": {"newRoot": "$doc"}
                }
                final_pipeline.append(replace_stage)

            # 添加用户定义的管道阶段
            final_pipeline.extend(sanitized_pipeline)

            # 数据精度处理：对浮点数字段进行四舍五入
            format_stage = {
                "$addFields": {
                    # 负荷数据保留3位小数
                    "LDC_1": {"$round": ["$LDC_1", 3]},
                    "LDC_2": {"$round": ["$LDC_2", 3]},
                    "LDC_3": {"$round": ["$LDC_3", 3]},
                    "LDC_4": {"$round": ["$LDC_4", 3]},
                    # 压力数据保留5位小数
                    "S5_01": {"$round": ["$S5_01", 5]},
                    "S5_02": {"$round": ["$S5_02", 5]},
                    "S5_0301": {"$round": ["$S5_0301", 3]},
                    "S5_0302": {"$round": ["$S5_0302", 5]},
                    "S5_0401": {"$round": ["$S5_0401", 5]},
                    "S5_0402": {"$round": ["$S5_0402", 5]},
                    # 温度数据保留3位小数
                    "FEED_T_HG": {"$round": ["$FEED_T_HG", 3]},
                    "FEED_T_STC": {"$round": ["$FEED_T_STC", 3]},
                    "FEED_T_NH": {"$round": ["$FEED_T_NH", 3]},
                    "BACK_T_HG": {"$round": ["$BACK_T_HG", 3]},
                    "BACK_T_STC": {"$round": ["$BACK_T_STC", 3]},
                    "BACK_T_NH": {"$round": ["$BACK_T_NH", 3]}
                }
            }
            final_pipeline.append(format_stage)

            # 如果没有 $limit，在尾部加一个保护性 limit
            has_limit = any("$limit" in st for st in pipeline)
            if not has_limit:
                final_pipeline.append({"$limit": limit})

            # 字段投影保护（可选）
            if projection:
                final_pipeline.append({"$project": projection})

            # 执行聚合查询
            collection_obj = SensorData._get_collection()
            timeout_ms = getattr(settings, 'AGENT_TIMEOUT_S', 20) * 1000
            data = list(collection_obj.aggregate(
                final_pipeline, 
                allowDiskUse=True,
                maxTimeMS=timeout_ms
            ))
            
            # 处理返回数据中的ObjectId和datetime
            for item in data:
                if '_id' in item:
                    item['_id'] = str(item['_id'])
                if 'timestamp' in item and hasattr(item['timestamp'], 'isoformat'):
                    item['timestamp'] = item['timestamp'].isoformat()
            
            # 准备返回的时间范围信息
            time_range_info = {}
            if tr:
                time_range_info = {
                    "start": tr["start"].isoformat(),
                    "end": tr["end"].isoformat()
                }

            return {
                "ok": True,
                "count": len(data),
                "data": data,
                "pipeline": final_pipeline,
                "time_range": time_range_info,
                "estimated_total_records": int((tr["end"] - tr["start"]).total_seconds() / 10) if tr else 0,
                "actual_time_range": time_range_info,
                "query_duration_seconds": (tr["end"] - tr["start"]).total_seconds() if tr else 0,
                "debug_info": {
                    "collection": collection,
                    "time_field": time_field,
                    "has_limit": has_limit,
                    "sample_interval": sample_interval,
                    "user_has_time_filter": False,
                    "time_format_used": "bj_naive_datetime",
                    "pipeline_stages": len(final_pipeline),
                    "data_exists": len(data) > 0
                }
            }
        else:
            return {"ok": False, "error": f"Collection {collection} not implemented yet"}
            
    except Exception as e:
        return {"ok": False, "error": str(e)}

def gen_chart_option(chart_type: str, data: List[Dict[str, Any]], encodings: Dict[str, Any]) -> Dict[str, Any]:
    """
    针对传感器数据优化的图表生成
    """
    if not data:
        raise ToolError("data cannot be empty")
    
    if not encodings:
        raise ToolError("encodings cannot be empty")
    
    x_key = encodings.get("x", "timestamp")
    y_keys = encodings.get("y")
    title = encodings.get("title", "数据趋势图")
    y_unit = encodings.get("y_unit", "")

    if not y_keys:
        raise ToolError("encodings must include y field(s)")

    # 支持单个字段或多个字段
    if isinstance(y_keys, str):
        y_keys = [y_keys]

    # 数据采样：如果数据点太多，进行智能采样
    max_points = 200  # 限制最大数据点数量
    if len(data) > max_points:
        # 按时间均匀采样
        step = len(data) // max_points
        data = data[::step]

    # 提取时间轴数据
    x_axis_data = []
    series_data = {field: [] for field in y_keys}

    for row in data:
        # 格式化时间显示
        timestamp = row.get(x_key)
        if isinstance(timestamp, str):
            try:
                ts = dt.datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                x_axis_data.append(ts.strftime("%m-%d %H:%M"))
            except:
                x_axis_data.append(str(timestamp))
        else:
            x_axis_data.append(str(timestamp))
        
        # 提取各字段数据
        for field in y_keys:
            value = row.get(field)
            series_data[field].append(value if value is not None else 0)

    # 生成系列配置
    series = []
    
    if chart_type == "pie":
        # 饼图特殊处理：需要将数据转换为饼图格式
        pie_data = []
        for field in y_keys:
            field_name = get_field_display_name(field)
            # 计算该字段的平均值或最新值作为饼图数据
            values = series_data[field]
            if values:
                # 使用平均值，如果都是0则使用最新值
                avg_value = sum(values) / len(values) if values else 0
                if avg_value == 0 and values:
                    avg_value = values[-1]  # 使用最新值
                if avg_value > 0:  # 只显示大于0的数据
                    pie_data.append({
                        "name": field_name,
                        "value": round(avg_value, 2)
                    })
        
        if not pie_data:
            raise ToolError("饼图数据为空，请确保至少有一个字段有有效数据")
            
        series.append({
            "name": title,
            "type": "pie",
            "radius": "50%",
            "data": pie_data,
            "emphasis": {
                "itemStyle": {
                    "shadowBlur": 10,
                    "shadowOffsetX": 0,
                    "shadowColor": "rgba(0, 0, 0, 0.5)"
                }
            }
        })
    else:
        # 其他图表类型的处理
        for field in y_keys:
            # 根据字段类型确定系列名称
            field_name = get_field_display_name(field)
            series_config = {
                "name": field_name,
                "data": series_data[field],
            }
            
            if chart_type == "line":
                series_config.update({
                    "type": "line",
                    "smooth": True,
                    "symbol": "none" if len(data) > 100 else "circle",
                    "lineWidth": 2
                })
            elif chart_type == "bar":
                series_config.update({
                    "type": "bar"
                })
            elif chart_type == "scatter":
                series_config.update({
                    "type": "scatter",
                    "symbolSize": 6
                })
            elif chart_type == "area":
                series_config.update({
                    "type": "line",
                    "smooth": True,
                    "areaStyle": {},
                    "symbol": "none" if len(data) > 100 else "circle",
                    "lineWidth": 2
                })
            
            series.append(series_config)

    # 生成ECharts配置
    if chart_type == "pie":
        # 饼图配置
        option = {
            "title": {
                "text": title,
                "left": "center",
                "textStyle": {"fontSize": 16}
            },
            "tooltip": {
                "trigger": "item",
                "formatter": "{a} <br/>{b}: {c} ({d}%)"
            },
            "legend": {
                "orient": "vertical",
                "left": "left",
                "data": [get_field_display_name(field) for field in y_keys]
            },
            "series": series
        }
    else:
        # 其他图表配置
        option = {
            "title": {
                "text": title,
                "left": "center",
                "textStyle": {"fontSize": 16}
            },
            "tooltip": {
                "trigger": "axis",
                "axisPointer": {"type": "cross"}
            },
            "legend": {
                "type": "scroll",
                "top": 30,
                "data": [get_field_display_name(field) for field in y_keys]
            },
            "grid": {
                "left": "3%",
                "right": "4%",
                "bottom": "3%",
                "containLabel": True
            },
            "xAxis": {
                "type": "category",
                "boundaryGap": False,
                "data": x_axis_data,
                "axisLabel": {"rotate": 45 if len(x_axis_data) > 20 else 0}
            },
            "yAxis": {
                "type": "value",
                "name": y_unit,
                "axisLabel": {"formatter": f"{{value}} {y_unit}"}
            },
            "series": series
        }
    
    # 如果数据点太多，添加数据缩放（饼图不需要）
    if chart_type != "pie" and len(data) > 50:
        option["dataZoom"] = [
            {"type": "inside", "start": 0, "end": 100},
            {"type": "slider", "start": 0, "end": 100, "height": 20}
        ]
    
    return option

def get_data_time_range(collection: str = "sensor_data") -> Dict[str, Any]:
    """
    获取数据的实际时间范围，用于无数据时的自适应查询
    """
    ensure_collection_allowed(collection)
    
    try:
        if collection == "sensor_data":
            # 获取最新和最旧的数据时间（更稳健：使用 find_one 而非 list 索引）
            collection_obj = SensorData._get_collection()

            latest_doc = collection_obj.find_one(sort=[("timestamp", -1)])
            oldest_doc = collection_obj.find_one(sort=[("timestamp", 1)])

            if latest_doc is None or oldest_doc is None:
                return {
                    "ok": False,
                    "error": "No data found in collection",
                    "collection": collection
                }

            latest_time = latest_doc.get("timestamp")
            oldest_time = oldest_doc.get("timestamp")

            total_count = collection_obj.count_documents({})

            return {
                "ok": True,
                "collection": collection,
                "latest_time": latest_time.isoformat() if hasattr(latest_time, 'isoformat') else str(latest_time),
                "oldest_time": oldest_time.isoformat() if hasattr(oldest_time, 'isoformat') else str(oldest_time),
                "total_records": total_count,
                "data_span_hours": (latest_time - oldest_time).total_seconds() / 3600 if latest_time and oldest_time else 0,
                "note": f"数据时间范围：{oldest_time} 到 {latest_time}，共{total_count}条记录"
            }
        else:
            return {"ok": False, "error": f"Collection {collection} not supported for time range detection"}
            
    except Exception as e:
        return {"ok": False, "error": str(e)}

def get_field_display_name(field: str) -> str:
    """获取字段的显示名称"""
    display_names = {
        "LDC_1": "1号机负荷",
        "LDC_2": "2号机负荷", 
        "LDC_3": "3号机负荷",
        "LDC_4": "4号机负荷",
        "S5_01": "1号机五抽压力",
        "S5_02": "2号机五抽压力",
        "S5_0301": "3号机五抽压力(1路)",
        "S5_0302": "3号机五抽压力(2路)",
        "S5_0401": "4号机五抽压力(1路)",
        "S5_0402": "4号机五抽压力(2路)",
        "FEED_T_HG": "汉沽供水温度",
        "FEED_T_STC": "生态城供水温度",
        "FEED_T_NH": "宁河供水温度",
        "BACK_T_HG": "汉沽回水温度",
        "BACK_T_STC": "生态城回水温度",
        "BACK_T_NH": "宁河回水温度"
    }
    return display_names.get(field, field)
