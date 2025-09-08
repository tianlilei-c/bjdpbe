from django.core.management.base import BaseCommand
from django.conf import settings
from datetime import datetime
import time
import requests

from dataservice.models import WeatherRecord


class Command(BaseCommand):
    help = '从百度天气API拉取天气信息并保存到MongoDB。默认一次；可 --continuous 周期拉取。'

    def add_arguments(self, parser):
        parser.add_argument('--district-id', type=str, help='行政区ID，默认 settings.BAIDU_WEATHER_DISTRICT_ID')
        parser.add_argument('--interval', type=int, default=3600, help='连续模式下的拉取间隔秒，默认3600(1小时)')
        parser.add_argument('--continuous', action='store_true', help='是否连续拉取')

    def handle(self, *args, **options):
        district_id: str = options.get('district_id') or getattr(settings, 'BAIDU_WEATHER_DISTRICT_ID', '120116')
        interval: int = options.get('interval', 3600)
        continuous: bool = options.get('continuous', False)

        ak = getattr(settings, 'BAIDU_WEATHER_AK', '')
        host = getattr(settings, 'BAIDU_WEATHER_HOST', 'https://api.map.baidu.com')
        uri = getattr(settings, 'BAIDU_WEATHER_URI', '/weather/v1/')
        if not ak:
            self.stdout.write(self.style.ERROR('BAIDU_WEATHER_AK 未配置'))
            return

        def fetch_once():
            try:
                params = {"district_id": district_id, "data_type": "all", "ak": ak}
                resp = requests.get(url=host + uri, params=params, timeout=10)
                if not resp.ok:
                    self.stdout.write(self.style.ERROR(f'HTTP {resp.status_code}'))
                    return False
                data = resp.json()
                if data.get('status') != 0:
                    self.stdout.write(self.style.ERROR(f'API error: {data}'))
                    return False

                result = data.get('result') or {}
                forecasts = result.get('forecasts') or []
                city = (result.get('location') or {}).get('city', '')

                today = forecasts[0] if len(forecasts) >= 1 else {}
                tomorrow = forecasts[1] if len(forecasts) >= 2 else {}

                data_date = datetime.strptime(today.get('date', datetime.now().strftime('%Y-%m-%d')), '%Y-%m-%d')

                rec = WeatherRecord.objects(district_id=district_id, data_date=data_date).first() or WeatherRecord(
                    district_id=district_id, data_date=data_date
                )
                rec.city_name = city
                rec.data_source = 'baidu'
                rec.today_text_day = today.get('text_day')
                rec.today_text_night = today.get('text_night')
                rec.today_wd_day = today.get('wd_day')
                rec.today_wc_day = today.get('wc_day')
                rec.today_wd_night = today.get('wd_night')
                rec.today_wc_night = today.get('wc_night')
                rec.today_low = _safe_int(today.get('low'))
                rec.today_high = _safe_int(today.get('high'))

                rec.tomorrow_text_day = tomorrow.get('text_day')
                rec.tomorrow_text_night = tomorrow.get('text_night')
                rec.tomorrow_wd_day = tomorrow.get('wd_day')
                rec.tomorrow_wc_day = tomorrow.get('wc_day')
                rec.tomorrow_wd_night = tomorrow.get('wd_night')
                rec.tomorrow_wc_night = tomorrow.get('wc_night')
                rec.tomorrow_low = _safe_int(tomorrow.get('low'))
                rec.tomorrow_high = _safe_int(tomorrow.get('high'))

                rec.raw_response = data
                rec.save()
                self.stdout.write(self.style.SUCCESS(f'天气数据已保存：{district_id} {data_date.date()}'))
                return True
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'抓取失败: {e}'))
                return False

        if not continuous:
            fetch_once()
            return

        try:
            while True:
                fetch_once()
                time.sleep(max(60, interval))
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('已停止连续拉取'))


def _safe_int(v):
    try:
        return int(v) if v is not None else None
    except Exception:
        try:
            return int(float(v))
        except Exception:
            return None


