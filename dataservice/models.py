from django.db import models
from mongoengine import Document, DateTimeField, FloatField, StringField, IntField, BooleanField
import datetime

# Create your models here.

class User(Document):
    """
    用户模型，用于登录认证
    """
    username = StringField(required=True, unique=True, max_length=50, verbose_name="用户名")
    password = StringField(required=True, max_length=128, verbose_name="密码")
    real_name = StringField(max_length=50, verbose_name="真实姓名")
    email = StringField(max_length=100, verbose_name="邮箱")
    roles = StringField(default="user", verbose_name="角色", help_text="角色：admin, user")
    is_active = BooleanField(default=True, verbose_name="是否激活")
    created_at = DateTimeField(default=datetime.datetime.now, verbose_name="创建时间")
    last_login = DateTimeField(verbose_name="最后登录时间")
    
    meta = {
        'collection': 'users',
        'indexes': ['username'],
        'ordering': ['-created_at']
    }
    
    def __str__(self):
        return self.username

class SensorData(Document):
    """
    传感器数据模型，对应yuan.csv中的数据结构
    """
    # 时间戳字段，用于数据查询和筛选
    timestamp = DateTimeField(required=True, default=datetime.datetime.now)
    
    # 机组负荷
    LDC_1 = FloatField(verbose_name="#1机负荷", help_text="sis取值，前端取整数")
    LDC_2 = FloatField(verbose_name="#2机负荷", help_text="sis取值，前端取整数")
    LDC_3 = FloatField(verbose_name="#3机负荷", help_text="sis取值，前端取整数")
    LDC_4 = FloatField(verbose_name="#4机负荷", help_text="sis取值，前端取整数")
    
    # 机组五抽压力
    S5_01 = FloatField(verbose_name="#1机五抽压力", help_text="sis取值，前端取3位小数")
    S5_02 = FloatField(verbose_name="#2机五抽压力", help_text="sis取值，前端取3位小数")
    S5_0301 = FloatField(verbose_name="#3机五抽一路压力", help_text="sis取值，前端取3位小数")
    S5_0302 = FloatField(verbose_name="#3机五抽二路压力", help_text="sis取值，前端取3位小数")
    S5_0401 = FloatField(verbose_name="#4机五抽一路压力", help_text="sis取值，前端取3位小数")
    S5_0402 = FloatField(verbose_name="#4机五抽二路压力", help_text="sis取值，前端取3位小数")
    
    # 供热计划
    PLAN_MONTH = FloatField(verbose_name="月供热计划", help_text="每月后台手动更新，整数，单位：万GJ")
    
    # 日供热量
    HEATSUP_DAY_HG = FloatField(verbose_name="汉沽日供热量", help_text="后台上传Excel文件或手动输入，单位：万GJ，前端取2位小数")
    HEATSUP_DAY_STC = FloatField(verbose_name="生态城日供热量", help_text="后台上传Excel文件或手动输入，单位：万GJ，前端取2位小数")
    HEATSUP_DAY_NH = FloatField(verbose_name="宁河日供热量", help_text="后台上传Excel文件或手动输入，单位：万GJ，前端取2位小数")
    STEAMSUP_DAY_YC = FloatField(verbose_name="盐场日供汽量", help_text="后台上传Excel文件或手动输入，单位：万GJ，前端取2位小数")
    
    # 累计热量
    HEATSUP_TOTAL_HG = FloatField(verbose_name="汉沽累计热量", help_text="sis取值，前端取整数")
    HEATSUP_TOTAL_STC = FloatField(verbose_name="生态城累计热量", help_text="sis取值，前端取整数")
    HEATSUP_TOTAL_NH = FloatField(verbose_name="宁河累计热量", help_text="sis取值，前端取整数")
    STEAMSUP_TOTAL_YC = FloatField(verbose_name="盐场累计供汽量", help_text="sis取值，前端取整数")
    
    # 供水流量
    FEED_FLOW_HG = FloatField(verbose_name="汉沽供水流量", help_text="sis取值，前端取整数")
    FEED_FLOW_STC = FloatField(verbose_name="生态城供水流量", help_text="sis取值，前端取整数")
    FEED_FLOW_NH = FloatField(verbose_name="宁河供水流量", help_text="sis取值，前端取整数")
    
    # 回水流量
    BACK_FLOW_HG = FloatField(verbose_name="汉沽回水流量", help_text="sis取值，前端取整数")
    BACK_FLOW_STC = FloatField(verbose_name="生态城回水流量", help_text="sis取值，前端取整数")
    BACK_FLOW_NH = FloatField(verbose_name="宁河回水流量", help_text="sis取值，前端取整数")
    
    # 供水压力
    FEED_P_HG = FloatField(verbose_name="汉沽供水压力", help_text="sis取值，前端取2位小数")
    FEED_P_STC = FloatField(verbose_name="生态城供水压力", help_text="sis取值，前端取2位小数")
    FEED_P_NH = FloatField(verbose_name="宁河供水压力", help_text="sis取值，前端取2位小数")
    
    # 回水压力
    BACK_P_HG = FloatField(verbose_name="汉沽回水压力", help_text="sis取值，前端取2位小数")
    BACK_P_STC = FloatField(verbose_name="生态城回水压力", help_text="sis取值，前端取2位小数")
    BACK_P_NH = FloatField(verbose_name="宁河回水压力", help_text="sis取值，前端取2位小数")
    
    # 实时热量
    HEATNOW_HG = FloatField(verbose_name="汉沽实时热量", help_text="sis取值，前端取整数")
    HEATNOW_STC = FloatField(verbose_name="生态城实时热量", help_text="sis取值，前端取整数")
    HEATNOW_NH = FloatField(verbose_name="宁河实时热量", help_text="sis取值，前端取整数")
    
    # 供水温度
    FEED_T_HG = FloatField(verbose_name="汉沽供水温度", help_text="sis取值，前端取整数")
    FEED_T_STC = FloatField(verbose_name="生态城供水温度", help_text="sis取值，前端取整数")
    FEED_T_NH = FloatField(verbose_name="宁河供水温度", help_text="sis取值，前端取整数")
    
    # 回水温度
    BACK_T_HG = FloatField(verbose_name="汉沽回水温度", help_text="sis取值，前端取整数")
    BACK_T_STC = FloatField(verbose_name="生态城回水温度", help_text="sis取值，前端取整数")
    BACK_T_NH = FloatField(verbose_name="宁河回水温度", help_text="sis取值，前端取整数")
    
    # 滨海热网疏水流量
    DRAIN_BH_03 = FloatField(verbose_name="#3机滨海热网疏水流量", help_text="sis取值,前端取2位小数")
    DRAIN_BH_04 = FloatField(verbose_name="#4机滨海热网疏水流量", help_text="sis取值,前端取2位小数")
    
    # 宁河热网疏水流量
    DRAIN_NH_03 = FloatField(verbose_name="#3机宁河热网疏水流量", help_text="sis取值,前端取2位小数")
    DRAIN_NH_04 = FloatField(verbose_name="#4机宁河热网疏水流量", help_text="sis取值,前端取2位小数")
    
    # 滨海热网补水流量
    MAKEUP_BH_N = FloatField(verbose_name="滨海热网正常补水流量", help_text="sis取值,前端取2位小数")
    MAKEUP_BH_N_TOTAL = FloatField(verbose_name="滨海热网正常补水流量累计", help_text="sis取值,前端取2位小数")
    MAKEUP_BH_E = FloatField(verbose_name="滨海热网事故补水流量", help_text="sis取值,前端取2位小数")
    MAKEUP_BH_E_TOTAL = FloatField(verbose_name="滨海热网事故补水流量累计", help_text="sis取值,前端取2位小数")
    
    # 宁河热网补水流量
    MAKEUP_NH_N = FloatField(verbose_name="宁河热网正常补水流量", help_text="sis取值,前端取2位小数")
    MAKEUP_NH_N_TOTAL = FloatField(verbose_name="宁河热网正常补水流量累计", help_text="sis取值,前端取2位小数")
    MAKEUP_NH_E = FloatField(verbose_name="宁河热网事故补水流量", help_text="sis取值,前端取2位小数")
    MAKEUP_NH_E_TOTAL = FloatField(verbose_name="宁河热网事故补水流量累计", help_text="sis取值,前端取2位小数")
    
    # 盐场实时流量
    STEAMNOW_YC = FloatField(verbose_name="盐场实时流量", help_text="sis取值,前端取2位小数")
    
    # 海淡抽汽流量
    U1_FLOW = FloatField(verbose_name="#1海淡抽汽流量", help_text="sis取值,前端取2位小数")
    U2_FLOW = FloatField(verbose_name="#2海淡抽汽流量", help_text="sis取值,前端取2位小数")
    U3_FLOW = FloatField(verbose_name="#3海淡抽汽流量", help_text="sis取值,前端取2位小数")
    U4_FLOW = FloatField(verbose_name="#4海淡抽汽流量", help_text="sis取值,前端取2位小数")
    U5_FLOW = FloatField(verbose_name="#5海淡抽汽流量", help_text="sis取值,前端取2位小数")
    U6_FLOW = FloatField(verbose_name="#6海淡抽汽流量", help_text="sis取值,前端取2位小数")
    U7_FLOW = FloatField(verbose_name="#7海淡抽汽流量", help_text="sis取值,前端取2位小数")
    U8_FLOW = FloatField(verbose_name="#8海淡抽汽流量", help_text="sis取值,前端取2位小数")
    
    # 热网首站
    F_STEAM_FLOW = FloatField(verbose_name="热网首站供汽流量", help_text="sis取值，前端取整数")
    F_DRAIN_FLOW = FloatField(verbose_name="热网首站疏水流量", help_text="sis取值，前端取整数") 
    F_FEED_T = FloatField(verbose_name="热网首站供水温度", help_text="sis取值，前端取整数")
    F_BACK_T = FloatField(verbose_name="热网首站回水温度", help_text="sis取值，前端取整数")
    
    meta = {
        'collection': 'sensor_data',  # 集合名称
        'indexes': [
            # 仅设置TTL过期时间，不设置background以避免参数冲突
            {
                'fields': ['timestamp'],
                'expireAfterSeconds': 94608000  # 3年 = 3*365*24*60*60 = 94608000秒
            },
            # 新增：按时间倒序的普通索引，优化“最新一条/时间段倒序”查询
            {
                'fields': ['-timestamp'],
                'name': 'ts_desc'
            }
        ],
        'ordering': ['-timestamp']  # 默认按时间降序排列
    }


class ManualPlan(Document):
    """
    月度手动计划（单位：万GJ）
    对应 需要的点.csv 中的 PLAN_MONTH
    唯一键：year + month
    """
    year = IntField(required=True, min_value=2000, max_value=2100, verbose_name="年")
    month = IntField(required=True, min_value=1, max_value=12, verbose_name="月")
    plan_month = FloatField(required=True, verbose_name="月供热计划(万GJ)")
    note = StringField(max_length=200, verbose_name="备注")
    created_by = StringField(max_length=50, verbose_name="创建人")
    created_at = DateTimeField(default=datetime.datetime.now, verbose_name="创建时间")
    updated_at = DateTimeField(default=datetime.datetime.now, verbose_name="更新时间")

    meta = {
        'collection': 'manual_plan',
        'indexes': [
            {'fields': ['year', 'month'], 'unique': True, 'name': 'uniq_year_month'}
        ],
        'ordering': ['-year', '-month']
    }

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super().save(*args, **kwargs)


class DailyManualData(Document):
    """
    日度手动数据（单位：万GJ）
    对应 需要的点.csv 中的 HEATSUP_DAY_* / STEAMSUP_DAY_YC
    唯一键：date（按天）
    """
    date = DateTimeField(required=True, verbose_name="日期(00:00:00)")
    HEATSUP_DAY_HG = FloatField(verbose_name="汉沽日供热量(万GJ)")
    HEATSUP_DAY_STC = FloatField(verbose_name="生态城日供热量(万GJ)")
    HEATSUP_DAY_NH = FloatField(verbose_name="宁河日供热量(万GJ)")
    STEAMSUP_DAY_YC = FloatField(verbose_name="盐场日供汽量(万GJ)")
    note = StringField(max_length=200, verbose_name="备注")
    created_by = StringField(max_length=50, verbose_name="创建人")
    created_at = DateTimeField(default=datetime.datetime.now, verbose_name="创建时间")
    updated_at = DateTimeField(default=datetime.datetime.now, verbose_name="更新时间")

    meta = {
        'collection': 'manual_day',
        'indexes': [
            {'fields': ['date'], 'unique': True, 'name': 'uniq_date'}
        ],
        'ordering': ['-date']
    }

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super().save(*args, **kwargs)
