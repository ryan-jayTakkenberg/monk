from django.urls import path
from .views import MealAnalyzeView, MealListView

urlpatterns = [
    path('', MealListView.as_view(), name='meals'),
    path('analyze/', MealAnalyzeView.as_view(), name='meals_analyze'),
]
