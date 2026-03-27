from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .models import JournalEntry, WeeklyRecap


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
        week_start = today - timezone.timedelta(days=today.weekday())
        week_end = week_start + timezone.timedelta(days=6)
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
