from django.db import models
from django.contrib.auth.models import User


class JournalEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='journal_entries')
    date = models.DateField()
    answer_1 = models.TextField()  # One thing to accomplish
    answer_2 = models.TextField()  # Energy and mindset
    answer_3 = models.TextField()  # What makes today a win
    answer_4 = models.TextField()  # Gratitude
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'date')
        ordering = ['-date']

    def __str__(self):
        return f'{self.user.username} — {self.date}'


class WeeklyRecap(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='weekly_recaps')
    week_start = models.DateField()
    ai_summary = models.TextField()
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'week_start')
        ordering = ['-week_start']

    def __str__(self):
        return f'{self.user.username} — week of {self.week_start}'
