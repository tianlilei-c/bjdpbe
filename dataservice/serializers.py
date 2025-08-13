from rest_framework import serializers
from .models import SensorData, ManualPlan, DailyManualData

class SensorDataSerializer(serializers.Serializer):
    """
    传感器数据序列化器，手动处理MongoEngine文档序列化
    """
    # 显式声明id字段
    id = serializers.CharField(read_only=True)
    
    # 使用ISO格式的时间戳
    timestamp = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    
    # 机组负荷
    LDC_1 = serializers.FloatField(required=False, allow_null=True)
    LDC_2 = serializers.FloatField(required=False, allow_null=True)
    LDC_3 = serializers.FloatField(required=False, allow_null=True)
    LDC_4 = serializers.FloatField(required=False, allow_null=True)
    
    # 机组五抽压力
    S5_01 = serializers.FloatField(required=False, allow_null=True)
    S5_02 = serializers.FloatField(required=False, allow_null=True)
    S5_0301 = serializers.FloatField(required=False, allow_null=True)
    S5_0302 = serializers.FloatField(required=False, allow_null=True)
    S5_0401 = serializers.FloatField(required=False, allow_null=True)
    S5_0402 = serializers.FloatField(required=False, allow_null=True)
    
    # 供热计划
    PLAN_MONTH = serializers.FloatField(required=False, allow_null=True)
    
    # 日供热量
    HEATSUP_DAY_HG = serializers.FloatField(required=False, allow_null=True)
    HEATSUP_DAY_STC = serializers.FloatField(required=False, allow_null=True)
    HEATSUP_DAY_NH = serializers.FloatField(required=False, allow_null=True)
    STEAMSUP_DAY_YC = serializers.FloatField(required=False, allow_null=True)
    
    # 累计热量
    HEATSUP_TOTAL_HG = serializers.FloatField(required=False, allow_null=True)
    HEATSUP_TOTAL_STC = serializers.FloatField(required=False, allow_null=True)
    HEATSUP_TOTAL_NH = serializers.FloatField(required=False, allow_null=True)
    STEAMSUP_TOTAL_YC = serializers.FloatField(required=False, allow_null=True)
    
    # 供水流量
    FEED_FLOW_HG = serializers.FloatField(required=False, allow_null=True)
    FEED_FLOW_STC = serializers.FloatField(required=False, allow_null=True)
    FEED_FLOW_NH = serializers.FloatField(required=False, allow_null=True)
    
    # 回水流量
    BACK_FLOW_HG = serializers.FloatField(required=False, allow_null=True)
    BACK_FLOW_STC = serializers.FloatField(required=False, allow_null=True)
    BACK_FLOW_NH = serializers.FloatField(required=False, allow_null=True)
    
    # 供水压力
    FEED_P_HG = serializers.FloatField(required=False, allow_null=True)
    FEED_P_STC = serializers.FloatField(required=False, allow_null=True)
    FEED_P_NH = serializers.FloatField(required=False, allow_null=True)
    
    # 回水压力
    BACK_P_HG = serializers.FloatField(required=False, allow_null=True)
    BACK_P_STC = serializers.FloatField(required=False, allow_null=True)
    BACK_P_NH = serializers.FloatField(required=False, allow_null=True)
    
    # 实时热量
    HEATNOW_HG = serializers.FloatField(required=False, allow_null=True)
    HEATNOW_STC = serializers.FloatField(required=False, allow_null=True)
    HEATNOW_NH = serializers.FloatField(required=False, allow_null=True)
    
    # 供水温度
    FEED_T_HG = serializers.FloatField(required=False, allow_null=True)
    FEED_T_STC = serializers.FloatField(required=False, allow_null=True)
    FEED_T_NH = serializers.FloatField(required=False, allow_null=True)
    
    # 回水温度
    BACK_T_HG = serializers.FloatField(required=False, allow_null=True)
    BACK_T_STC = serializers.FloatField(required=False, allow_null=True)
    BACK_T_NH = serializers.FloatField(required=False, allow_null=True)
    
    # 滨海热网疏水流量
    DRAIN_BH_03 = serializers.FloatField(required=False, allow_null=True)
    DRAIN_BH_04 = serializers.FloatField(required=False, allow_null=True)
    
    # 宁河热网疏水流量
    DRAIN_NH_03 = serializers.FloatField(required=False, allow_null=True)
    DRAIN_NH_04 = serializers.FloatField(required=False, allow_null=True)
    
    # 滨海热网补水流量
    MAKEUP_BH_N = serializers.FloatField(required=False, allow_null=True)
    MAKEUP_BH_N_TOTAL = serializers.FloatField(required=False, allow_null=True)
    MAKEUP_BH_E = serializers.FloatField(required=False, allow_null=True)
    MAKEUP_BH_E_TOTAL = serializers.FloatField(required=False, allow_null=True)
    
    # 宁河热网补水流量
    MAKEUP_NH_N = serializers.FloatField(required=False, allow_null=True)
    MAKEUP_NH_N_TOTAL = serializers.FloatField(required=False, allow_null=True)
    MAKEUP_NH_E = serializers.FloatField(required=False, allow_null=True)
    MAKEUP_NH_E_TOTAL = serializers.FloatField(required=False, allow_null=True)
    
    # 盐场实时流量
    STEAMNOW_YC = serializers.FloatField(required=False, allow_null=True)
    
    # 海淡抽汽流量
    U1_FLOW = serializers.FloatField(required=False, allow_null=True)
    U2_FLOW = serializers.FloatField(required=False, allow_null=True)
    U3_FLOW = serializers.FloatField(required=False, allow_null=True)
    U4_FLOW = serializers.FloatField(required=False, allow_null=True)
    U5_FLOW = serializers.FloatField(required=False, allow_null=True)
    U6_FLOW = serializers.FloatField(required=False, allow_null=True)
    U7_FLOW = serializers.FloatField(required=False, allow_null=True)
    U8_FLOW = serializers.FloatField(required=False, allow_null=True)
    
    # 热网首站
    F_STEAM_FLOW = serializers.FloatField(required=False, allow_null=True)
    F_DRAIN_FLOW = serializers.FloatField(required=False, allow_null=True)
    F_FEED_T = serializers.FloatField(required=False, allow_null=True)
    F_BACK_T = serializers.FloatField(required=False, allow_null=True)
    
    def to_representation(self, instance):
        """
        将MongoEngine文档实例转换为字典
        """
        if instance is None:
            return None
            
        data = {}
        # 添加id字段
        data['id'] = str(instance.id) if hasattr(instance, 'id') and instance.id else None
        
        # 处理所有字段
        field_names = [
            'timestamp', 'LDC_1', 'LDC_2', 'LDC_3', 'LDC_4',
            'S5_01', 'S5_02', 'S5_0301', 'S5_0302', 'S5_0401', 'S5_0402',
            'PLAN_MONTH', 'HEATSUP_DAY_HG', 'HEATSUP_DAY_STC', 'HEATSUP_DAY_NH', 
            'STEAMSUP_DAY_YC', 'HEATSUP_TOTAL_HG', 'HEATSUP_TOTAL_STC', 
            'HEATSUP_TOTAL_NH', 'STEAMSUP_TOTAL_YC', 'FEED_FLOW_HG', 
            'FEED_FLOW_STC', 'FEED_FLOW_NH', 'BACK_FLOW_HG', 'BACK_FLOW_STC', 
            'BACK_FLOW_NH', 'FEED_P_HG', 'FEED_P_STC', 'FEED_P_NH', 
            'BACK_P_HG', 'BACK_P_STC', 'BACK_P_NH', 'HEATNOW_HG', 
            'HEATNOW_STC', 'HEATNOW_NH', 'FEED_T_HG', 'FEED_T_STC', 
            'FEED_T_NH', 'BACK_T_HG', 'BACK_T_STC', 'BACK_T_NH',
            'DRAIN_BH_03', 'DRAIN_BH_04', 'DRAIN_NH_03', 'DRAIN_NH_04',
            'MAKEUP_BH_N', 'MAKEUP_BH_N_TOTAL', 'MAKEUP_BH_E', 'MAKEUP_BH_E_TOTAL',
            'MAKEUP_NH_N', 'MAKEUP_NH_N_TOTAL', 'MAKEUP_NH_E', 'MAKEUP_NH_E_TOTAL',
            'STEAMNOW_YC', 'U1_FLOW', 'U2_FLOW', 'U3_FLOW', 'U4_FLOW',
            'U5_FLOW', 'U6_FLOW', 'U7_FLOW', 'U8_FLOW', 'F_STEAM_FLOW',
            'F_DRAIN_FLOW', 'F_FEED_T', 'F_BACK_T'
        ]
        
        for field_name in field_names:
            if hasattr(instance, field_name):
                value = getattr(instance, field_name)
                if field_name == 'timestamp' and value:
                    # 格式化时间戳
                    data[field_name] = value.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    data[field_name] = value
            else:
                data[field_name] = None
                
        return data
    
    def create(self, validated_data):
        """
        创建并返回新的SensorData实例
        """
        return SensorData.objects.create(**validated_data)
        
    def update(self, instance, validated_data):
        """
        根据提供的验证数据更新并返回现有的SensorData实例
        """
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance 


class ManualPlanSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    year = serializers.IntegerField()
    month = serializers.IntegerField()
    plan_month = serializers.FloatField()
    note = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    created_by = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def to_representation(self, instance):
        if instance is None:
            return None
        return {
            'id': str(instance.id),
            'year': instance.year,
            'month': instance.month,
            'plan_month': instance.plan_month,
            'note': getattr(instance, 'note', None),
            'created_by': getattr(instance, 'created_by', None),
            'created_at': instance.created_at.isoformat() if instance.created_at else None,
            'updated_at': instance.updated_at.isoformat() if instance.updated_at else None,
        }

    def create(self, validated_data):
        return ManualPlan.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for k, v in validated_data.items():
            setattr(instance, k, v)
        instance.save()
        return instance


class DailyManualDataSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    date = serializers.DateTimeField(format="%Y-%m-%d")
    HEATSUP_DAY_HG = serializers.FloatField(required=False, allow_null=True)
    HEATSUP_DAY_STC = serializers.FloatField(required=False, allow_null=True)
    HEATSUP_DAY_NH = serializers.FloatField(required=False, allow_null=True)
    STEAMSUP_DAY_YC = serializers.FloatField(required=False, allow_null=True)
    note = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    created_by = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def to_representation(self, instance):
        if instance is None:
            return None
        return {
            'id': str(instance.id),
            'date': instance.date.strftime('%Y-%m-%d') if instance.date else None,
            'HEATSUP_DAY_HG': getattr(instance, 'HEATSUP_DAY_HG', None),
            'HEATSUP_DAY_STC': getattr(instance, 'HEATSUP_DAY_STC', None),
            'HEATSUP_DAY_NH': getattr(instance, 'HEATSUP_DAY_NH', None),
            'STEAMSUP_DAY_YC': getattr(instance, 'STEAMSUP_DAY_YC', None),
            'note': getattr(instance, 'note', None),
            'created_by': getattr(instance, 'created_by', None),
            'created_at': instance.created_at.isoformat() if instance.created_at else None,
            'updated_at': instance.updated_at.isoformat() if instance.updated_at else None,
        }

    def create(self, validated_data):
        return DailyManualData.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for k, v in validated_data.items():
            setattr(instance, k, v)
        instance.save()
        return instance