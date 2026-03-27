from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import WhoopToken, WhoopSleepRecord


class WhoopStatusView(APIView):
    def get(self, request):
        connected = WhoopToken.objects.filter(user=request.user).exists()
        if not connected:
            return Response({'connected': False, 'data': None})

        record = WhoopSleepRecord.objects.filter(user=request.user).first()
        if not record:
            return Response({'connected': True, 'data': None})

        return Response({
            'connected': True,
            'data': {
                'recorded_date': record.recorded_date,
                'duration_hours': record.duration_hours,
                'awake_pct': record.awake_pct,
                'light_pct': record.light_pct,
                'deep_pct': record.deep_pct,
                'recovery_score': record.recovery_score,
                'hrv': record.hrv,
            }
        })
