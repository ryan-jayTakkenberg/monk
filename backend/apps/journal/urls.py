from django.urls import path
from .views import JournalTodayView, JournalWeekView, WeeklyRecapView

urlpatterns = [
    path('', JournalTodayView.as_view(), name='journal'),
    path('week/', JournalWeekView.as_view(), name='journal_week'),
    path('recap/', WeeklyRecapView.as_view(), name='journal_recap'),
]
