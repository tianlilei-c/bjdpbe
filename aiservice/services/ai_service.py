import os
import json
from typing import Dict, Any
from django.conf import settings
# backend\aiservice\agent.py
from ..agent import run_agent, run_simple_query

class AIDataService:
    def __init__(self):
        self.api_key = getattr(settings, 'DEEPSEEKKEY', None)
        
    def analyze_data_with_agent(self, query: str, debug: bool = True) -> Dict[str, Any]:
        """
        使用Agent分析数据
        
        Args:
            query: 用户查询
            debug: 是否返回调试信息
        """
        try:
            # 优先使用完整的Agent
            if self.api_key:
                result = run_agent(query, debug=debug)
            else:
                # 降级到简单查询
                result = run_simple_query(query)
                
            return result
            
        except Exception as e:
            # 如果Agent失败，降级到简单查询
            try:
                return run_simple_query(query)
            except Exception as fallback_e:
                return {
                    "final": {
                        "type": "text",
                        "content": f"分析失败: {str(e)}\n降级查询也失败: {str(fallback_e)}"
                    }
                }

    def analyze_data(self, query: str, context_hours: int = 24) -> str:
        """兼容旧接口的分析方法"""
        result = self.analyze_data_with_agent(query)
        
        if result.get("final", {}).get("type") == "text":
            return result["final"]["content"]
        else:
            return "AI分析完成，请查看图表或表格结果"

    def generate_chart_config(self, data_type: str, time_range: int = 24) -> Dict[str, Any]:
        """生成图表配置"""
        # 基于data_type生成查询
        if data_type == "load":
            query = f"显示最近{time_range}小时的机组负荷趋势"
        elif data_type == "pressure":
            query = f"显示最近{time_range}小时的五抽压力变化"
        elif data_type == "temperature":
            query = f"显示最近{time_range}小时的供水温度趋势"
        else:
            query = f"显示最近{time_range}小时的数据趋势"
            
        result = self.analyze_data_with_agent(query)
        
        if result.get("final", {}).get("type") == "chart":
            return result["final"]["option"]
        else:
            # 返回默认配置
            return {
                "title": {"text": "数据图表", "left": "center"},
                "tooltip": {"trigger": "axis"},
                "xAxis": {"type": "category", "data": []},
                "yAxis": {"type": "value"},
                "series": [{"type": "line", "data": []}]
            }
