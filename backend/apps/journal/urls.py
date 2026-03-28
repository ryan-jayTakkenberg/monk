from django.urls import path
from .views import JournalTodayView, JournalWeekView, WeeklyRecapView, WeeklyRecapHistoryView

urlpatterns = [
    path('', JournalTodayView.as_view(), name='journal'),
    path('week/', JournalWeekView.as_view(), name='journal_week'),
    path('recap/history/', WeeklyRecapHistoryView.as_view(), name='journal_recap_history'),
    path('recap/', WeeklyRecapView.as_view(), name='journal_recap'),
]
