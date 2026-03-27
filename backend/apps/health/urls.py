from django.urls import path
from .views import WhoopStatusView

urlpatterns = [
    path('status/', WhoopStatusView.as_view(), name='whoop_status'),
]
