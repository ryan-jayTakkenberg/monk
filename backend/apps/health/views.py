from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .models import WhoopToken, WhoopSleepRecord
from services.claude import generate_suggestions


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


class WhoopSyncView(APIView):
    def get(self, request):
        import requests

        try:
            token = WhoopToken.objects.get(user=request.user)
        except WhoopToken.DoesNotExist:
            return Response(
                {'error': 'Whoop not connected.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        headers = {'Authorization': f'Bearer {token.access_token}'}

        try:
            recovery_resp = requests.get(
                'https://api.prod.whoop.com/developer/v1/recovery',
                headers=headers
            )
            sleep_resp = requests.get(
                'https://api.prod.whoop.com/developer/v1/activity/sleep',
                headers=headers
            )
        except Exception:
            return Response(
                {'error': 'Sync failed.'},
                status=status.HTTP_502_BAD_GATEWAY
            )

        if recovery_resp.status_code == 401 or sleep_resp.status_code == 401:
            return Response(
                {'error': 'Whoop token expired. Reconnect.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            recovery_data = recovery_resp.json()
            sleep_data = sleep_resp.json()

            # Parse recovery fields
            recovery_records = recovery_data.get('records', [])
            latest_recovery = recovery_records[0] if recovery_records else {}
            recovery_score = latest_recovery.get('score', {}).get('recovery_score', None)
            hrv = latest_recovery.get('score', {}).get('hrv_rmssd_milli', None)

            # Parse sleep fields
            sleep_records = sleep_data.get('records', [])
            latest_sleep = sleep_records[0] if sleep_records else {}
            total_in_bed_milli = latest_sleep.get('score', {}).get('total_in_bed_time_milli', 0)
            duration_hours = round(total_in_bed_milli / 3_600_000, 2) if total_in_bed_milli else None

            sleep_score = latest_sleep.get('score', {})
            awake_pct = sleep_score.get('sleep_performance_percentage', {}).get('awake_pct', None) if isinstance(sleep_score.get('sleep_performance_percentage'), dict) else sleep_score.get('awake_pct', None)
            light_pct = sleep_score.get('light_pct', None)
            deep_pct = sleep_score.get('slow_wave_sleep_pct', None)

            today = timezone.localdate()

            record, _ = WhoopSleepRecord.objects.update_or_create(
                user=request.user,
                recorded_date=today,
                defaults={
                    'duration_hours': duration_hours,
                    'recovery_score': recovery_score,
                    'hrv': hrv,
                    'awake_pct': awake_pct,
                    'light_pct': light_pct,
                    'deep_pct': deep_pct,
                }
            )

            return Response({
                'recorded_date': record.recorded_date,
                'duration_hours': record.duration_hours,
                'recovery_score': record.recovery_score,
                'hrv': record.hrv,
                'awake_pct': record.awake_pct,
                'light_pct': record.light_pct,
                'deep_pct': record.deep_pct,
            })

        except Exception:
            return Response(
                {'error': 'Sync failed.'},
                status=status.HTTP_502_BAD_GATEWAY
            )


class HealthHistoryView(APIView):
    def get(self, request):
        from datetime import date, timedelta
        today = date.today()
        week_ago = today - timedelta(days=6)
        records = WhoopSleepRecord.objects.filter(
            user=request.user,
            recorded_date__range=(week_ago, today)
        ).order_by('recorded_date')
        return Response([{
            'date': r.recorded_date,
            'recovery_score': r.recovery_score,
            'duration_hours': r.duration_hours,
            'hrv': r.hrv,
            'deep_pct': r.deep_pct,
        } for r in records])


class SuggestionsView(APIView):
    def get(self, request):
        from django.db.models import Sum
        from apps.food.models import Meal

        today = timezone.localdate()

        # Get today's meal totals
        meal_totals = Meal.objects.filter(
            user=request.user,
            logged_at__date=today
        ).aggregate(
            total_kcal=Sum('kcal'),
            total_protein=Sum('protein_g')
        )
        kcal = meal_totals['total_kcal'] or 0
        protein = meal_totals['total_protein'] or 0

        # Get latest sleep record
        record = WhoopSleepRecord.objects.filter(user=request.user).order_by('-recorded_date').first()
        recovery = record.recovery_score if record and record.recovery_score is not None else 'unknown'
        hrv = record.hrv if record and record.hrv is not None else 'unknown'
        sleep_h = record.duration_hours if record and record.duration_hours is not None else 'unknown'

        try:
            suggestions = generate_suggestions(recovery, hrv, sleep_h, kcal, protein)
            return Response(suggestions)
        except Exception:
            return Response(
                {'error': 'Suggestions unavailable.'},
                status=status.HTTP_502_BAD_GATEWAY
            )
