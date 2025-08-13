from django.apps import AppConfig
from django.conf import settings
from mongoengine import connect


class DataserviceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dataservice'

    def ready(self):
        """在应用就绪时初始化 MongoEngine 连接（带认证）。"""
        # 使用副本，避免修改 settings 原始字典
        cfg = dict(getattr(settings, 'MONGODB_SETTINGS', {}) or {})
        # 复制并弹出 db 名称，剩余作为 connect 的关键字参数
        db_name = cfg.pop('db', None)
        if not db_name:
            return
        try:
            # 允许 settings 中传入 host/port/username/password/authentication_source 等
            connect(db=db_name, **cfg)
        except Exception:
            # 避免应用启动失败；具体错误在首次访问数据库时会显现
            pass
