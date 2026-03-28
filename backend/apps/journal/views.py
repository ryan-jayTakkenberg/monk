from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from .models import JournalEntry, WeeklyRecap
from services.claude import generate_weekly_recap


class JournalTodayView(APIView):
    def get(self, request):
        today = timezone.localdate()
        entry = JournalEntry.objects.filter(user=request.user, date=today).first()
        if not entry:
            return Response({'completed': False, 'entry': None})
        return Response({
            'completed': True,
            'entry': {
                'id': entry.id,
                'date': entry.date,
                'answer_1': entry.answer_1,
                'answer_2': entry.answer_2,
                'answer_3': entry.answer_3,
                'answer_4': entry.answer_4,
            }
        })

    def post(self, request):
        today = timezone.localdate()
        entry, _ = JournalEntry.objects.update_or_create(
            user=request.user,
            date=today,
            defaults={
                'answer_1': request.data.get('answer_1', ''),
                'answer_2': request.data.get('answer_2', ''),
                'answer_3': request.data.get('answer_3', ''),
                'answer_4': request.data.get('answer_4', ''),
            }
        )
        return Response({'id': entry.id, 'date': entry.date}, status=status.HTTP_201_CREATED)


class JournalWeekView(APIView):
    def get(self, request):
        today = timezone.localdate()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        entries = JournalEntry.objects.filter(
            user=request.user,
            date__range=(week_start, week_end)
        )
        return Response([{
            'id': e.id,
            'date': e.date,
            'answer_1': e.answer_1,
            'answer_2': e.answer_2,
            'answer_3': e.answer_3,
            'answer_4': e.answer_4,
        } for e in entries])


class WeeklyRecapView(APIView):
    def get(self, request):
        today = timezone.localdate()
        week_start = today - timedelta(days=today.weekday())

        recap = WeeklyRecap.objects.filter(
            user=request.user,
            week_start=week_start
        ).first()

        if not recap:
            return Response({'recap': None})

        return Response({
            'recap': recap.ai_summary,
            'generated_at': recap.generated_at,
        })

    def post(self, request):
        today = timezone.localdate()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)

        entries = JournalEntry.objects.filter(
            user=request.user,
            date__range=(week_start, week_end)
        ).order_by('date')

        if not entries.exists():
            return Response(
                {'error': 'No journal entries this week.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            ai_summary = generate_weekly_recap(list(entries))
        except Exception:
            return Response(
                {'error': 'Recap generation failed.'},
                status=status.HTTP_502_BAD_GATEWAY
            )

        recap, _ = WeeklyRecap.objects.update_or_create(
            user=request.user,
            week_start=week_start,
            defaults={'ai_summary': ai_summary}
        )

        return Response({
            'recap': recap.ai_summary,
            'generated_at': recap.generated_at,
        })


class WeeklyRecapHistoryView(APIView):
    def get(self, request):
        recaps = WeeklyRecap.objects.filter(user=request.user).order_by('-week_start')
        return Response([{
            'week_start': r.week_start,
            'ai_summary': r.ai_summary,
            'generated_at': r.generated_at,
        } for r in recaps])
