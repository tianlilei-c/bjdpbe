"""
保留示例脚本，但建议改用 management command：
python manage.py fetch_weather --continuous --interval 3600
或通过 /api/weather/fetch_once 触发一次。
"""

import os
import requests

host = os.getenv('BAIDU_WEATHER_HOST', 'https://api.map.baidu.com')
uri = os.getenv('BAIDU_WEATHER_URI', '/weather/v1/')
ak = os.getenv('BAIDU_WEATHER_AK', '')
district_id = os.getenv('BAIDU_WEATHER_DISTRICT_ID', '120116')

if not ak:
    print('请设置环境变量 BAIDU_WEATHER_AK')
else:
    params = {"district_id": district_id, "data_type": "all", "ak": ak}
    response = requests.get(url=host + uri, params=params, timeout=10)
    if response.ok:
        data = response.json()
        if data.get("status") == 0:
            today = (data.get("result") or {}).get("forecasts", [{}])[0]
            print(f"{today.get('date')} {today.get('week', '')}：白天{today.get('text_day')}，"
                  f"夜间{today.get('text_night')}，气温 {today.get('low')}~{today.get('high')}°C，"
                  f"白天{today.get('wd_day')} {today.get('wc_day')}，夜间{today.get('wd_night')} {today.get('wc_night')}")
        else:
            print("API 返回错误：", data)
    else:
        print("请求失败：", response.status_code)
