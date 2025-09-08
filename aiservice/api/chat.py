from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from ..services.ai_service import AIDataService

class AgentAskView(APIView):
    """
    新的Agent接口，完全基于新方案
    """
    permission_classes = []
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ai_service = AIDataService()
    
    def post(self, request):
        """
        Agent问答接口
        
        请求体格式:
        {
            "query": "对比4台机组最近24小时的负荷趋势",
            "debug": true  # 可选，是否返回调试信息
        }
        """
        query = request.data.get('query', '').strip()
        debug = request.data.get('debug', True)  # 默认开启调试
        
        if not query:
            return Response(
                {"error": "query required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            result = self.ai_service.analyze_data_with_agent(query, debug=debug)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"final": {"type": "text", "content": f"Agent执行错误: {str(e)}"}},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
