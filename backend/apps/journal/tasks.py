from celery import shared_task
from django.utils import timezone
from datetime import timedelta


@shared_task
def generate_weekly_recaps():
    """Runs every Sunday at 20:00. Generates a WeeklyRecap for every user who has journal entries this week."""
    from django.contrib.auth.models import User
    from apps.journal.models import JournalEntry, WeeklyRecap
    from services.claude import generate_weekly_recap

    today = timezone.localdate()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)

    for user in User.objects.filter(is_active=True):
        entries = list(JournalEntry.objects.filter(
            user=user, date__range=(week_start, week_end)
        ).order_by('date'))

        if not entries:
            continue

        try:
            summary = generate_weekly_recap(entries)
            WeeklyRecap.objects.update_or_create(
                user=user, week_start=week_start,
                defaults={'ai_summary': summary}
            )
        except Exception:
            pass  # Don't let one user's failure block others
