from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
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
        import anthropic
        from django.conf import settings

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

        journal_text = ''
        for e in entries:
            journal_text += (
                f'Date: {e.date}\n'
                f'One thing to accomplish: {e.answer_1}\n'
                f'Energy and mindset: {e.answer_2}\n'
                f'What makes today a win: {e.answer_3}\n'
                f'Gratitude: {e.answer_4}\n\n'
            )

        try:
            client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            message = client.messages.create(
                model='claude-sonnet-4-6',
                max_tokens=300,
                messages=[{
                    'role': 'user',
                    'content': (
                        'You are a direct, no-nonsense coach writing a weekly recap for a man. '
                        'Based on his journal entries below, write 3-4 sentences. '
                        'Be honest, specific, mention patterns you notice. No fluff, no softness.\n\n'
                        f'{journal_text}'
                    )
                }]
            )
            ai_summary = message.content[0].text
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
