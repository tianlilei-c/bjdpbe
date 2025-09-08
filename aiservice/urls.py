from django.urls import path
from .api.chat import AgentAskView

urlpatterns = [

    # 新的Agent接口
    path('agent/ask/', AgentAskView.as_view(), name='agent_ask'),
]
