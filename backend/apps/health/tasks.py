from celery import shared_task
from django.utils import timezone


@shared_task
def sync_all_whoop():
    """Runs nightly at 06:00. Syncs Whoop data for all users with a valid token."""
    from apps.health.models import WhoopToken, WhoopSleepRecord
    from services.whoop import get_today_data

    today = timezone.localdate()

    for token in WhoopToken.objects.select_related('user').all():
        try:
            data = get_today_data(token.access_token)
            WhoopSleepRecord.objects.update_or_create(
                user=token.user, recorded_date=today,
                defaults=data
            )
        except PermissionError:
            pass  # Token expired — user needs to reconnect
        except Exception:
            pass  # Network error etc — will retry next run
