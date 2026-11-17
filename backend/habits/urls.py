from django.urls import path
from .views import HabitListCreateView, HabitDetailView, HabitCheckView, HabitStatsView

urlpatterns = [
    path('', HabitListCreateView.as_view(), name='habit_list_create'),
    path('stats/', HabitStatsView.as_view(), name='habit_stats'),
    path('<int:pk>/', HabitDetailView.as_view(), name='habit_detail'),
    path('<int:pk>/check/', HabitCheckView.as_view(), name='habit_check'),
]
