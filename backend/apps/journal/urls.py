from django.urls import path
from .views import JournalTodayView, JournalWeekView

urlpatterns = [
    path('', JournalTodayView.as_view(), name='journal'),
    path('week/', JournalWeekView.as_view(), name='journal_week'),
]
