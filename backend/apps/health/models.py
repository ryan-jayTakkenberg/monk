from django.db import models
from django.contrib.auth.models import User


class WhoopToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='whoop_token')
    access_token = models.TextField()
    refresh_token = models.TextField()
    expires_at = models.DateTimeField()

    def __str__(self):
        return f'{self.user.username} — Whoop token'


class WhoopSleepRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sleep_records')
    recorded_date = models.DateField()
    duration_hours = models.FloatField()
    awake_pct = models.FloatField(default=0)
    light_pct = models.FloatField(default=0)
    deep_pct = models.FloatField(default=0)
    recovery_score = models.IntegerField(default=0)  # 0-100
    hrv = models.FloatField(default=0)
    synced_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'recorded_date')
        ordering = ['-recorded_date']

    def __str__(self):
        return f'{self.user.username} — {self.recorded_date} ({self.recovery_score}% recovery)'
