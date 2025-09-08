# apps/aiservice/agent.py
# Tracing edition: show every step of the agent-tool loop to the client when debug=True
import json
from typing import Any, Dict, List, Optional
from django.conf import settings
import requests
from .tools import (
    describe_schema,
    run_aggregation,
    gen_chart_option,
    get_data_time_range,
    ToolError,
)

SYSTEM_PROMPT = """
你是一个工业数据分析助手。你不能直接访问数据库。
你只有两种行为：
A) 发起工具调用（function call）
B) 在所有工具完成后，输出严格 JSON：{"final": {...}}。不得包含其他字符或自然语言。

工具使用规则：
1) 仅允许使用集合：sensor_data。不要编造新的集合名。
2) 若需要字段/样本/集合信息，必须先调用 describe_schema；
3) 若需要数据，必须调用 run_aggregation；不要在 pipeline 中自行编写针对 timestamp 的 $match 过滤，统一通过 time_range 传参，时间默认均为北京时间；
4) 若查询返回0条数据，可调用 get_data_time_range 检查数据时间范围；
5) 若需要图表，必须调用 gen_chart_option。参数说明：
   - chart_type: 图表类型，如"line"（必需）
   - data: 数据数组，从 run_aggregation 返回的 data 字段获取（必需）
   - encodings: 编码配置，包含：
     * x: X轴字段名，默认为"timestamp"（可选）
     * y: Y轴字段名数组，如["FEED_T_HG", "FEED_T_STC"]（必需）
     * title: 图表标题（可选）
     * y_unit: Y轴单位，如"°C"（可选）

时间查询建议（均以北京时间解释）：
- 默认查询最近24小时
- 用户口述“X月Y日”且未指明年份时，优先按当前年解释
- 避免在 pipeline 中自行写时间匹配；一律通过 time_range
- 如果查询无结果，先查询实际数据时间范围并给出合适建议
- 高频数据（10秒采集）会自动按分钟级采样，减少数据量

仅允许以下最终输出其一：
- {"final": {"type": "chart", "option": {...}, "explain": "..."}}
- {"final": {"type": "table", "columns": [...], "rows": [...], "explain": "..."}}
- {"final": {"type": "text", "content": "..."}}
"""

TOOLS: Dict[str, Dict[str, Any]] = {
    "describe_schema": {
        "name": "describe_schema",
        "desc": "List allowed collections and sample fields",
        "schema": {
            "type": "object",
            "properties": {
                "collection": {"type": "string", "enum": ["sensor_data"], "default": "sensor_data"}
            }
        },
    },
    "run_aggregation": {
        "name": "run_aggregation",
        "desc": "Run a MongoDB aggregation pipeline safely on sensor data",
        "schema": {
            "type": "object",
            "properties": {
                "collection": {"type": "string", "enum": ["sensor_data"]},
                "pipeline": {"type": "array", "items": {"type": "object"}},
                "limit": {"type": "integer", "maximum": 5000},
                "projection": {"type": "object"},
                "time_range": {
                    "type": "object",
                    "properties": {
                        "start": {"type": "string"},
                        "end": {"type": "string"},
                    },
                },
                "time_field": {"type": "string", "default": "timestamp"},
                "sample_interval": {"type": "integer"},
            },
            "required": ["collection", "pipeline"],
        },
    },
    "get_data_time_range": {
        "name": "get_data_time_range",
        "desc": "Get actual data time range when no data found in specified range",
        "schema": {
            "type": "object",
            "properties": {
                "collection": {"type": "string", "enum": ["sensor_data"], "default": "sensor_data"}
            },
        },
    },
    "gen_chart_option": {
        "name": "gen_chart_option",
        "desc": "Generate ECharts option from sensor data",
        "schema": {
            "type": "object",
            "properties": {
                "chart_type": {"type": "string", "enum": ["line", "bar", "scatter", "area", "pie"], "description": "图表类型，如'line'"},
                "data": {"type": "array", "description": "数据数组，每个元素是一个包含字段值的数据对象"},
                "encodings": {
                    "type": "object",
                    "properties": {
                        "x": {"type": "string", "default": "timestamp", "description": "X轴字段名，默认为timestamp"},
                        "y": {"type": "array", "items": {"type": "string"}, "description": "Y轴字段名数组，如['FEED_T_HG', 'FEED_T_STC']"},
                        "title": {"type": "string", "description": "图表标题"},
                        "y_unit": {"type": "string", "description": "Y轴单位，如'°C', 'MW'"},
                    },
                    "required": ["y"],
                },
            },
            "required": ["chart_type", "data", "encodings"],
        },
    },
}

def _build_tools_list(tools: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [
        {
            "type": "function",
            "function": {
                "name": v["name"],
                "description": v["desc"],
                "parameters": v["schema"],
            },
        }
        for v in tools.values()
    ]

def call_deepseek(
    messages: List[Dict[str, Any]],
    tools: Optional[Dict[str, Any]] = None,
    *,
    force_tool: Optional[str] = None,
    json_only: bool = True,
    trace: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """OpenAI 兼容调用；支持首轮强制工具、严格 JSON、写入 trace。"""
    print("=== Call DeepSeek ===")
    api_key = getattr(settings, "DEEPSEEKKEY", "")
    if not api_key:
        return {"error": "DEEPSEEK_API_KEY not configured"}

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    payload: Dict[str, Any] = {
        "model": getattr(settings, "DEEPSEEK_MODEL", "deepseek-chat"),  # 建议先用 chat 模型做工具调度
        "messages": messages,
        "temperature": 0.1,
        "max_tokens": 3000,
    }
    if tools:
        payload["tools"] = _build_tools_list(tools)
        payload["tool_choice"] = {"type": "function", "function": {"name": force_tool}} if force_tool else "auto"
    if json_only:
        payload["response_format"] = {"type": "json_object"}

    # 获取超时配置
    timeout_seconds = getattr(settings, "DEEPSEEK_TIMEOUT", 120)
    api_url = getattr(settings, "DEEPSEEK_API_URL", "https://api.deepseek.com/chat/completions")
    
    # 详细的请求日志
    request_info = {
        "url": api_url,
        "timeout": timeout_seconds,
        "model": payload.get("model"),
        "messages_count": len(messages),
        "has_tools": bool(tools),
        "force_tool": force_tool,
        "json_only": json_only,
        "payload_size": len(str(payload)),
        "last_message": messages[-1] if messages else None,
    }
    
    print(f"=== DeepSeek Request Details ===")
    print(f"URL: {api_url}")
    print(f"Timeout: {timeout_seconds}s")
    print(f"Model: {payload.get('model')}")
    print(f"Messages count: {len(messages)}")
    print(f"Has tools: {bool(tools)}")
    print(f"Force tool: {force_tool}")
    print(f"JSON only: {json_only}")
    print(f"Payload size: {len(str(payload))} chars")
    if messages:
        print(f"Last message role: {messages[-1].get('role', 'unknown')}")
        print(f"Last message content length: {len(str(messages[-1].get('content', '')))}")
    print("=" * 50)

    if trace is not None:
        trace.append({
            "stage": "api_request",
            "force_tool": force_tool or "auto",
            "json_only": json_only,
            "messages_tail": messages[-2:],  # 只记录最后两条，避免日志过大与暴露敏感
            "request_info": request_info,
        })

    try:
        print(f"=== Sending request to DeepSeek API ===")
        resp = requests.post(api_url, headers=headers, json=payload, timeout=timeout_seconds)
        
        print(f"=== DeepSeek Response ===")
        print(f"Status code: {resp.status_code}")
        print(f"Response size: {len(resp.text)} chars")
        print(f"Response headers: {dict(resp.headers)}")
        
        if trace is not None:
            trace.append({
                "stage": "api_response_meta",
                "status_code": resp.status_code,
                "ok": resp.status_code == 200,
                "response_size": len(resp.text),
                "response_headers": dict(resp.headers),
            })
            
        if resp.status_code == 200:
            try:
                response_json = resp.json()
                print(f"Response parsed successfully, keys: {list(response_json.keys())}")
                return response_json
            except Exception as parse_error:
                print(f"Failed to parse JSON response: {parse_error}")
                print(f"Response text (first 500 chars): {resp.text[:500]}")
                return {"error": f"Failed to parse JSON response: {parse_error}"}
        else:
            print(f"API error response: {resp.text[:500]}")
            return {"error": f"API call failed with status {resp.status_code}: {resp.text}"}
            
    except requests.exceptions.Timeout as timeout_error:
        error_msg = f"API call timed out after {timeout_seconds}s: {timeout_error}"
        print(f"=== TIMEOUT ERROR ===")
        print(error_msg)
        print(f"Request was: {request_info}")
        if trace is not None:
            trace.append({
                "stage": "api_timeout",
                "timeout_seconds": timeout_seconds,
                "request_info": request_info,
                "error": str(timeout_error),
            })
        return {"error": error_msg}
        
    except requests.exceptions.ConnectionError as conn_error:
        error_msg = f"API connection error: {conn_error}"
        print(f"=== CONNECTION ERROR ===")
        print(error_msg)
        print(f"Request was: {request_info}")
        if trace is not None:
            trace.append({
                "stage": "api_connection_error",
                "request_info": request_info,
                "error": str(conn_error),
            })
        return {"error": error_msg}
        
    except Exception as e:
        error_msg = f"API call failed: {e}"
        print(f"=== GENERAL ERROR ===")
        print(error_msg)
        print(f"Request was: {request_info}")
        if trace is not None:
            trace.append({
                "stage": "api_general_error",
                "request_info": request_info,
                "error": str(e),
            })
        return {"error": error_msg}

def _exec_tool(name: str, args: Dict[str, Any], trace: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """执行工具并写入精简 trace。"""
    try:
        if trace is not None:
            trace.append({"stage": "tool_call", "name": name, "args": _redact_args(args)})

        # 移除时间格式转换 - 让tools.py直接处理datetime对象
        # MongoDB查询需要使用datetime对象而不是字符串

        if name == "describe_schema":
            result = describe_schema(**args)
        elif name == "run_aggregation":
            result = run_aggregation(**args)
        elif name == "get_data_time_range":
            result = get_data_time_range(**args)
        elif name == "gen_chart_option":
            result = gen_chart_option(**args)
        else:
            result = {"ok": False, "error": f"Unknown tool {name}"}

        if trace is not None:
            trace.append({
                "stage": "tool_result",
                "name": name,
                "summary": _summarize_result(result),
            })
        return result
    except ToolError as e:
        err = {"ok": False, "error": str(e)}
        if trace is not None:
            trace.append({"stage": "tool_error", "name": name, "error": str(e)})
        return err
    except Exception as e:
        err = {"ok": False, "error": f"Internal tool error: {e}"}
        if trace is not None:
            trace.append({"stage": "tool_error", "name": name, "error": str(e)})
        return err

def _redact_args(args: Dict[str, Any]) -> Dict[str, Any]:
    """避免把超长 pipeline/敏感字段全量塞进 trace，这里做浅层摘要。"""
    out = dict(args or {})
    if "pipeline" in out:
        try:
            out["pipeline_len"] = len(out["pipeline"])
            out["pipeline_preview"] = out["pipeline"][:2]
            del out["pipeline"]
        except Exception:
            pass
    return out

def _summarize_result(result: Dict[str, Any]) -> Dict[str, Any]:
    """把工具结果压成简短元信息，避免 trace 过大。"""
    if not isinstance(result, dict):
        return {"type": type(result).__name__}
    summary = {}
    for k in ("ok", "error", "count", "pipeline", "time_range", "collection"):
        if k in result:
            summary[k] = result[k] if k != "pipeline" else f"len={len(result[k])}"
    if "data" in result:
        summary["data_len"] = len(result.get("data") or [])
        if result.get("data"):
            sample = result["data"][0]
            # 只保留首行的几个关键字段
            summary["data_sample_keys"] = list(sample.keys())[:6]
    return summary

def run_agent(user_query: str, *, max_iterations: int = 6, debug: bool = True) -> Dict[str, Any]:
    """
    主执行循环：首轮强制 describe_schema；全程追踪 trace；必要时降级。
    """
    trace: List[Dict[str, Any]] = []
    messages: List[Dict[str, Any]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_query},
    ]
    trace.append({"stage": "start", "query": user_query})

    # 第1轮：强制 describe_schema（避免模型只回"让我看看…"的文本）
    resp = call_deepseek(messages, TOOLS, force_tool="describe_schema", json_only=True, trace=trace)
    if "error" in resp:
        result = {"final": {"type": "text", "content": f"API错误: {resp['error']}"}}
        # 即使API失败，也返回trace信息以便调试
        return _with_debug(result, trace, debug=True)  # 强制返回debug信息

    if "choices" not in resp or not resp["choices"]:
        result = {"final": {"type": "text", "content": "API返回格式异常"}}
        return _with_debug(result, trace, debug)

    first_msg = resp["choices"][0]["message"]
    messages.append(first_msg)
    trace.append({"stage": "model_msg", "has_tool_calls": "tool_calls" in first_msg})

    # 执行首轮工具（如果有）
    if "tool_calls" in first_msg:
        for tc in first_msg["tool_calls"]:
            name = tc["function"]["name"]
            try:
                args = json.loads(tc["function"].get("arguments", "{}"))
            except json.JSONDecodeError:
                args = {}
            result = _exec_tool(name, args, trace)
            messages.append({
                "role": "tool",
                "tool_call_id": tc["id"],
                "name": name,
                "content": json.dumps(result, ensure_ascii=False, default=str),
            })
    else:
        # 没有 tool_calls：后端直接注入一次 schema 结果
        schema = describe_schema("sensor_data")
        trace.append({"stage": "forced_schema_inject"})
        messages.append({
            "role": "tool",
            "tool_call_id": "forced_describe_schema_1",
            "name": "describe_schema",
            "content": json.dumps(schema, ensure_ascii=False, default=str),
        })

    # 后续迭代
    iteration = 1
    while iteration < max_iterations:
        iteration += 1
        resp = call_deepseek(messages, TOOLS, json_only=True, trace=trace)
        if "error" in resp:
            result = {"final": {"type": "text", "content": f"API错误: {resp['error']}"}}
            # 即使API失败，也返回trace信息以便调试
            return _with_debug(result, trace, debug=True)  # 强制返回debug信息
        if "choices" not in resp or not resp["choices"]:
            result = {"final": {"type": "text", "content": "API返回格式异常"}}
            return _with_debug(result, trace, debug)

        msg = resp["choices"][0]["message"]
        messages.append(msg)
        trace.append({"stage": "model_msg", "has_tool_calls": "tool_calls" in msg})

        if "tool_calls" in msg:
            for tc in msg["tool_calls"]:
                name = tc["function"]["name"]
                try:
                    args = json.loads(tc["function"].get("arguments", "{}"))
                except json.JSONDecodeError:
                    args = {}
                result = _exec_tool(name, args, trace)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "name": name,
                    "content": json.dumps(result, ensure_ascii=False, default=str),
                })
            continue  # 继续下一轮，让模型基于工具结果产生 final

        # 没有 tool_calls：尝试直接要最终 JSON
        final_try = call_deepseek(messages, TOOLS, json_only=False, trace=trace)
        if "error" in final_try:
            result = {"final": {"type": "text", "content": f"最终API错误: {final_try['error']}"}}
            return _with_debug(result, trace, debug=True)  # 强制返回debug信息
        if "choices" in final_try and final_try["choices"]:
            final_text = final_try["choices"][0]["message"].get("content", "").strip()

            # 尝试解析最终结果
            if final_text.startswith("{"):
                try:
                    # 清理可能的格式问题
                    cleaned_text = final_text.strip()
                    # 如果JSON被截断，尝试找到完整的JSON
                    if not cleaned_text.endswith("}"):
                        # 找到最后一个完整的JSON对象
                        brace_count = 0
                        end_pos = -1
                        for i, char in enumerate(cleaned_text):
                            if char == "{":
                                brace_count += 1
                            elif char == "}":
                                brace_count -= 1
                                if brace_count == 0:
                                    end_pos = i + 1
                                    break
                        if end_pos > 0:
                            cleaned_text = cleaned_text[:end_pos]
                    
                    result = json.loads(cleaned_text)
                    if "final" in result:
                        return _with_debug(result, trace, debug)
                except Exception as e:
                    trace.append({"stage": "json_parse_error", "error": str(e), "text": final_text[:200]})

            # 如果解析失败，添加提示重新生成
            messages.append({
                "role": "user",
                "content": "请根据已返回的工具结果，输出严格 JSON格式的最终结果，不要任何其他字符。格式：{\"final\": {\"type\": \"chart\", \"option\": {...}, \"explain\": \"...\"}}",
            })
            trace.append({"stage": "json_retry"})
            continue

    # 多轮仍未成功：降级
    fallback = run_simple_query(user_query)
    trace.append({"stage": "fallback", "reason": "max_iterations_reached"})
    return _with_debug(fallback, trace, debug)

def _with_debug(result: Dict[str, Any], trace: List[Dict[str, Any]], debug: bool) -> Dict[str, Any]:
    """把 trace 装入返回体（仅 debug=True 时）。"""
    if debug:
        result = dict(result)
        result["debug"] = {"trace": trace}
    return result

def run_simple_query(user_query: str) -> Dict[str, Any]:
    """降级：固定给最近6小时负荷图，避免空手而回。"""
    import datetime as dt
    try:
        # 使用北京时间
        tz_bj = dt.timezone(dt.timedelta(hours=8))
        now_bj = dt.datetime.now(tz_bj).replace(tzinfo=None)

        pipeline = [{"$sort": {"timestamp": -1}}, {"$limit": 360}]
        result = run_aggregation(
            collection="sensor_data",
            pipeline=pipeline,
            time_range={
                "start": (now_bj - dt.timedelta(hours=6)).isoformat(),
                "end": now_bj.isoformat(),
            },
        )
        if result.get("ok") and result.get("data"):
            option = gen_chart_option(
                chart_type="line",
                data=result["data"],
                encodings={
                    "y": ["LDC_1", "LDC_2", "LDC_3", "LDC_4"],
                    "title": "Unit Load (Last 6h)",
                    "y_unit": "MW",
                },
            )
            return {"final": {"type": "chart", "option": option, "explain": "查询无结果，回退为最近6小时负荷图，"}}
        return {"final": {"type": "text", "content": "降级：未查询到数据。请缩短时间范围或检查数据采集状态。"}}
    except Exception as e:
        return {"final": {"type": "text", "content": f"降级查询失败：{e}"}}
