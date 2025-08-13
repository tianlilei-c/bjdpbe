# encoding:utf-8
import requests

# 服务地址
host = "https://api.map.baidu.com"
# 接口地址
uri = "/weather/v1/"
ak = "QbcyAz5VAPXxHYGOtHBwuE7y8pFjCPnK"

params = {
    "district_id": "120116",  # 滨海新区
    "data_type": "all",       # 返回全部类型数据
    "ak": ak,
}

response = requests.get(url=host + uri, params=params)
if response.ok:
    data = response.json()
    if data.get("status") == 0:
        today = data["result"]["forecasts"][0]  # 只取第一天
        print(f"{today['date']} {today['week']}：白天{today['text_day']}，"
              f"夜间{today['text_night']}，气温 {today['low']}~{today['high']}°C，"
              f"白天{today['wd_day']} {today['wc_day']}，夜间{today['wd_night']} {today['wc_night']}")
    else:
        print("API 返回错误：", data)
else:
    print("请求失败：", response.status_code)
