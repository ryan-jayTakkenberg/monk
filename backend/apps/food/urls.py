from django.urls import path
from .views import MealAnalyzeView, MealListView, MealDetailView

urlpatterns = [
    path('', MealListView.as_view(), name='meals'),
    path('analyze/', MealAnalyzeView.as_view(), name='meals_analyze'),
    path('<int:pk>/', MealDetailView.as_view(), name='meal_detail'),
]
