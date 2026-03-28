from django.urls import path
from .views import WhoopStatusView, WhoopSyncView, SuggestionsView, HealthHistoryView

urlpatterns = [
    path('status/', WhoopStatusView.as_view(), name='whoop_status'),
    path('sync/', WhoopSyncView.as_view(), name='whoop_sync'),
    path('suggestions/', SuggestionsView.as_view(), name='health_suggestions'),
    path('history/', HealthHistoryView.as_view(), name='health_history'),
]
