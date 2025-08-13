import time
import random
from django.core.management.base import BaseCommand
from django.conf import settings
from datetime import datetime
import logging

from dataservice.models import SensorData

class Command(BaseCommand):
    help = '从外部源获取数据（当前为模拟数据）并存储到MongoDB'

    # 基准数据，从CSV文件中提取的值
    base_data = {
        "LDC_1": 928.77,
        "LDC_2": 864.25,
        "LDC_3": 993.11,
        "LDC_4": 665.55,
        "S5_01": 0.463,
        "S5_02": 0.426,
        "S5_0301": 0.501,
        "S5_0302": 0.492,
        "S5_0401": 0.387,
        "S5_0402": 0.379,
        "PLAN_MONTH": 175,
        "HEATSUP_DAY_HG": 1.965426,
        "HEATSUP_DAY_STC": 1.582567,
        "HEATSUP_DAY_NH": 1.356724,
        "STEAMSUP_DAY_YC": 1242.346473,
        "HEATSUP_TOTAL_HG": 0,
        "HEATSUP_TOTAL_STC": 0,
        "HEATSUP_TOTAL_NH": 0,
        "STEAMSUP_TOTAL_YC": 0,
        "FEED_FLOW_HG": 3592.46,
        "FEED_FLOW_STC": 3305.23,
        "FEED_FLOW_NH": 2933.65,
        "BACK_FLOW_HG": 3581.36,
        "BACK_FLOW_STC": 3277.24,
        "BACK_FLOW_NH": 2931.32,
        "FEED_P_HG": 0.77,
        "FEED_P_STC": 0.77,
        "FEED_P_NH": 0.93,
        "BACK_P_HG": 0.27,
        "BACK_P_STC": 0.27,
        "BACK_P_NH": 0.32,
        "HEATNOW_HG": 928.23,
        "HEATNOW_STC": 901.43,
        "HEATNOW_NH": 856.36,
        "FEED_T_HG": 98.34,
        "FEED_T_STC": 98.22,
        "FEED_T_NH": 102.87,
        "BACK_T_HG": 46.32,
        "BACK_T_STC": 51.61,
        "BACK_T_NH": 48.24,
        "DRAIN_BH_03": 277.34,
        "DRAIN_BH_04": 293.41,
        "DRAIN_NH_03": 0,
        "DRAIN_NH_04": 311.64,
        "MAKEUP_BH_N": 74.55,
        "MAKEUP_BH_N_TOTAL": 56346.43,
        "MAKEUP_BH_E": 0,
        "MAKEUP_BH_E_TOTAL": 2432.54,
        "MAKEUP_NH_N": 22.78,
        "MAKEUP_NH_N_TOTAL": 5853.33,
        "MAKEUP_NH_E": 0,
        "MAKEUP_NH_E_TOTAL": 691.48,
        "STEAMNOW_YC": 55.26,
        "U1_FLOW": 0,
        "U2_FLOW": 0,
        "U3_FLOW": 48.34,
        "U4_FLOW": 49.62,
        "U5_FLOW": 0,
        "U6_FLOW": 48.97,
        "U7_FLOW": 0,
        "U8_FLOW": 0,
        "F_STEAM_FLOW": 136.22,
        "F_DRAIN_FLOW": 138.73,
        "F_FEED_T": 93.47,
        "F_BACK_T": 48.45
    }

    def add_arguments(self, parser):
        parser.add_argument(
            '--continuous',
            action='store_true',
            help='连续运行，每10秒获取一次数据',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('开始生成传感器数据...'))
        
        # 尝试保存一条简单的测试数据
        try:
            test_data = SensorData(timestamp=datetime.now())
            test_data.LDC_1 = 100.0
            test_data.save()
            self.stdout.write(self.style.SUCCESS('成功保存测试数据'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'保存测试数据失败: {e}'))
        
        # 检查是否连续运行
        if options['continuous']:
            try:
                while True:
                    try:
                        data = self.generate_and_save_data()
                        self.stdout.write(self.style.SUCCESS(f'成功生成模拟数据，时间: {datetime.now()}'))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'生成数据失败: {e}'))
                    # 等待10秒
                    time.sleep(10)
            except KeyboardInterrupt:
                self.stdout.write(self.style.WARNING('数据生成已停止'))
        else:
            # 单次运行
            try:
                self.generate_and_save_data()
                self.stdout.write(self.style.SUCCESS('成功生成模拟数据'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'生成数据失败: {e}'))

    def generate_and_save_data(self):
        """
        生成模拟数据并保存
        """
        # 创建新的SensorData对象
        sensor_data = SensorData(timestamp=datetime.now())
        
        # 为每个字段生成模拟数据（在基准值基础上浮动±5个点）
        for field, base_value in self.base_data.items():
            if base_value is not None:  # 只处理有基准值的字段
                # 随机浮动-5到+5之间的值
                fluctuation = random.uniform(-5, 5)
                new_value = base_value + fluctuation
                
                # 确保值不为负数（如果原始值较小）
                if base_value > 5:
                    new_value = max(0, new_value)
                    
                # 设置字段值
                setattr(sensor_data, field, new_value)
        
        # 输出调试信息
        self.stdout.write(self.style.SUCCESS(f'准备保存数据: {sensor_data.timestamp}'))
        
        # 保存到MongoDB
        try:
            sensor_data.save()
            self.stdout.write(self.style.SUCCESS('数据保存成功'))
            return sensor_data
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'保存数据时出错: {str(e)}'))
            raise 